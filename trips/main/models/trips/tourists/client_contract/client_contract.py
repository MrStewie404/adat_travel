from datetime import date
from decimal import Decimal

from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models, transaction

from main.models.agency.agency import Agency
from main.models.clients.client import Client
from main.models.clients.coupons.coupon_label import CouponLabel
from main.models.fields.random_slug_field import RandomSlugField
from main.models.trips.tourists.trip_company import TripCompany
from main.models.utils import create_price_field
from main.utils.utils import truncate_str_custom


class ClientContractManager(models.Manager):
    def get_by_natural_key(self, contract_number, agency__name):
        return self.get(
            contract_number=contract_number,
            trip_company__trip__agency=Agency.objects.get_by_natural_key(agency__name),
        )


class ClientContract(models.Model):
    """Договор с клиентом"""

    trip_company = models.OneToOneField(TripCompany, on_delete=models.CASCADE, related_name='client_contract')
    customer = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='client_contracts')
    services = models.ManyToManyField('Service', through='ClientContractAndService', related_name='client_contracts',
                                      blank=True)
    slug = RandomSlugField('Строковый идентификатор')
    contract_number = models.CharField('Номер договора', max_length=32)
    base_price = create_price_field('Базовая стоимость')
    discount = create_price_field('Скидка', default=0)
    prepayment = create_price_field('Предоплата', default=0)
    sign_date = models.DateField('Дата подписания', default=date.today)
    tourists_count = models.PositiveSmallIntegerField('Количество гостей', blank=True, null=True,
                                                      validators=[MinValueValidator(1)])
    contract_template = models.CharField('Шаблон договора', max_length=128, blank=True)

    objects = ClientContractManager()

    def natural_key(self):
        return (self.contract_number,) + self.trip_company.trip.agency.natural_key()

    natural_key.dependencies = ['main.tripcompany', 'main.trip', 'main.agency']

    @property
    def trip(self):
        return self.trip_company.trip

    def __str__(self):
        return f"Договор {self.contract_number} ({self.sign_date.strftime('%d.%m.%Y')}): {self.customer}"

    def contract_remaining(self):
        return self.total_price - self.prepayment

    def real_remaining(self):
        return self.total_price - self.total_paid_amount()

    def real_prepayment(self):
        from main.models.money.payment import Payment
        return Payment.get_expenses_sum(self.prepayment_expense_items(), is_outgoing=False)

    def remaining_amount_for_guide(self):
        amount = self.contract_remaining()
        paid_amount = self.paid_amount_for_guide()
        return amount - paid_amount

    def extra_services_price(self):
        prices = [x.total_price() for x in self.clientcontractandservice_set.all()]
        return sum(prices, Decimal(0))

    @property
    def total_price(self):
        # TODO: переписать с использованием trip_money_utils
        return self.base_price + self.extra_services_price() - self.discount

    def total_paid_amount(self):
        from main.models.money.client_contract_service_expense_item import ClientContractServiceExpenseItem
        from main.models.money.payment import Payment
        amount = Payment.get_expenses_sum(self.payment_expense_items.all(), is_outgoing=False)
        amount += Payment.get_expenses_sum(
            ClientContractServiceExpenseItem.objects.filter(contract_and_service__contract=self),
            is_outgoing=False,
        )
        return amount

    def paid_amount_for_guide(self):
        from main.models.money.payment import Payment
        expense_item = Payment.get_expense_item_for_guide(self.payment_expense_items, self.trip.agency,
                                                          is_outgoing=False)
        return expense_item.amount if expense_item else Decimal(0)

    def expense_item_for_guide(self):
        from main.models.money.payment import Payment
        return Payment.get_expense_item_for_guide(self.payment_expense_items, self.trip.agency, is_outgoing=False)

    def prepayment_expense_items(self):
        from main.models.money.payment import Payment
        return Payment.filter_expense_items_not_for_guide(
            self.payment_expense_items.filter(payment__payment_date__lte=self.trip.start_date),
            self.trip.agency,
            is_outgoing=False,
        ).order_by('payment__payment_date')

    def commission_estimate(self):
        return self.trip_company.commission_estimate()

    def final_tourists_count(self):
        if self.tourists_count:
            return self.tourists_count
        return self.trip_company.final_expected_tourists_count()

    def auto_bind_promo_code(self):
        from main.models.clients.coupons.coupon_usage_in_trip import CouponUsageInTrip

        # Если промокод уже привязан к договору или тур уже завершился, то выходим
        if self.used_promo_code() or self.trip_company.trip.is_finished():
            return

        trip = self.trip_company.trip
        coupon_referral = self.customer.get_valid_referral_coupon_for(trip)
        if coupon_referral:
            CouponUsageInTrip(coupon=coupon_referral, contract=self).save()

    def is_new_customer(self):
        return self.customer.is_new_customer(exclude_trip=self.trip_company.trip)

    def used_promo_code(self):
        usage = self.used_coupons.filter(coupon__label__label_type=CouponLabel.LabelTypeEnum.PROMO_CODE).first()
        return usage.coupon if usage else None

    def used_certificate(self):
        usage = self.used_coupons.filter(coupon__label__label_type=CouponLabel.LabelTypeEnum.CERTIFICATE).first()
        return usage.coupon if usage else None

    def save(self, *args, **kwargs):
        is_new = not self.pk
        super().save(*args, **kwargs)
        if is_new:
            self.auto_bind_promo_code()

    def add_service(self, service, trip_day, cost, price_type=None):
        from main.models.trips.tourists.client_contract.client_contract_and_service import ClientContractAndService
        contract_and_service = ClientContractAndService.objects.create(
            contract=self,
            service=service,
            trip_day=trip_day,
            tourist_count=self.final_tourists_count(),
            cost=cost,
        )
        if price_type is not None:
            contract_and_service.price_type = price_type
            contract_and_service.save()
        return contract_and_service

    def add_payment(self, owner, payment_amount, contract_part_amount, is_prepayment,
                    payment_date=None, payer=None, account=None, uploaded_file=None):
        from main.models.money.payment import Payment
        with transaction.atomic():
            agency = self.trip.agency
            payer = payer or self.customer.as_payment_party(save=True)
            purpose_prefix = "Предоплата" if is_prepayment else "Окончательный расчет"
            payment = Payment.objects.create(
                agency=agency,
                owner=owner,
                payer=payer,
                account=account,
                payment_date=payment_date if payment_date else date.today(),
                recipient=agency.as_payment_party(save=True),
                is_outgoing=False,
                amount=payment_amount,
                purpose_text=f"{purpose_prefix} по договору {truncate_str_custom(self.contract_number, 32)}",
                trip=self.trip,
            )

            payment.add_client_contract_expense_item(self, contract_part_amount)

            if uploaded_file:
                from main.models.money.payment_media import PaymentMedia
                PaymentMedia.create_check(payment=payment, file=uploaded_file)

            return payment

    def validate_unique(self, exclude=None):
        super().validate_unique(exclude=exclude)
        agency = self.trip_company.trip.agency
        if ClientContract.objects.exclude(pk=self.pk).filter(
            trip_company__trip__agency=agency,
            contract_number=self.contract_number,
        ).exists():
            raise ValidationError("Договор с таким номером уже существует.", code='contract_number_not_unique')

    class Meta:
        verbose_name = 'Договор'
        verbose_name_plural = 'Договоры'
