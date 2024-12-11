from datetime import date
from decimal import Decimal

from django.core.validators import MinValueValidator
from django.db import models, transaction
from django.db.models import UniqueConstraint

from main.models.clients.client import Client
from main.models.services.supplier import Supplier, CommissionTypeEnum
from main.models.trips.departure_point import DeparturePoint
from main.models.trips.trip import Trip
from main.models.utils import create_price_field
from main.utils.utils import truncate_str_custom


class TripCompanyManager(models.Manager):
    def get_by_natural_key(self, trip__name, trip__start_date, trip__agency, *tourist_args):
        tourists_selector = []
        # Туриста нам могут не передать, см. комментарий в методе natural_key.
        if len(tourist_args) > 0:
            tourists_selector.append(Client.objects.get_by_natural_key(*tourist_args))
        return self.get(
            trip=Trip.objects.get_by_natural_key(trip__name, trip__start_date, trip__agency),
            tourists__in=tourists_selector,
        )


class TripCompany(models.Model):
    """Компания туристов на поездку. Внутри тур. группы люди могут объединяться в компании;
    это может быть пара, семья, друзья и т.п. Для них планируется, например, совместное проживание.
    """

    class AccommodationTypeEnum(models.TextChoices):
        NONE = 'NONE', '—'
        SINGLE = 'SINGLE', '1-местный (без подселения)'
        SINGLE_BIG_BED = 'SINGLE_BIG_BED', '1-местный с большой кроватью'
        SINGLE_WITH_SHARING = 'SINGLE_WITH_SHARING', '1 место в 2-местном'
        DOUBLE = 'DOUBLE', '2-местный (любой)'
        DOUBLE_TWIN_BEDS = 'DOUBLE_TWIN_BEDS', '2-местный с раздельными кроватями'
        DOUBLE_BIG_BED = 'DOUBLE_BIG_BED', '2-местный с большой кроватью'
        TRIPLE = 'TRIPLE', '3-местный (любой)'
        TRIPLE_THREE_BEDS = 'TRIPLE_THREE_BEDS', '3-местный с раздельными кроватями'
        TRIPLE_BIG_BED = 'TRIPLE_BIG_BED', '3-местный с большой кроватью'
        QUAD = 'QUAD', '4-местный (любой)'
        TWO_DOUBLE_ROOMS = 'TWO_DOUBLE_ROOMS', 'Два 2-местных номера'

    trip = models.ForeignKey(Trip, on_delete=models.CASCADE, related_name='trip_companies')
    tourists = models.ManyToManyField(Client, related_name='trip_companies', blank=True)
    name = models.CharField('Уникальное имя (в рамках одного тура)', max_length=32)  # Для fixtures-ов
    # TODO: по-хорошему, это поле надо бы перенести в договор
    desired_room_type = models.CharField(
        'Тип размещения (по договору)',
        max_length=32,
        choices=AccommodationTypeEnum.choices,
        default=AccommodationTypeEnum.NONE,
        blank=False,
    )
    expected_tourists_count = models.PositiveSmallIntegerField('Ожидаемое количество гостей', blank=True, null=True,
                                                               validators=[MinValueValidator(1)])
    departure_point = models.ForeignKey(DeparturePoint, on_delete=models.SET_NULL, blank=True, null=True,
                                        related_name='trip_companies')
    supplier = models.ForeignKey(Supplier, on_delete=models.SET_NULL, blank=True, null=True, related_name='trip_companies')
    supplier_commission = create_price_field('Величина комиссии', default=0)
    commission_type = models.PositiveSmallIntegerField(
        'Вид комиссии',
        choices=CommissionTypeEnum.choices,
        default=CommissionTypeEnum.PERCENT,
    )
    is_created_by_external_user = models.BooleanField('Самозапись', default=False)
    is_draft = models.BooleanField('Черновик/Заявка', default=False)
    has_children_pre7 = models.BooleanField('Дети до 7 лет', default=False)

    objects = TripCompanyManager()

    def natural_key(self):
        natural_key = self.trip.natural_key()
        # Django при десериализации вызывает natural_key() у модели, в которой ещё нет ни pk, ни полей many-to-many.
        if self.pk and self.tourists.exists():
            natural_key = natural_key + self.tourists.first().natural_key()
        return natural_key

    natural_key.dependencies = ['main.trip', 'main.client']

    def __str__(self):
        return f"{self.trip}, {self.name}, {self.get_desired_room_type_display()}"

    def tourists_count(self):
        """Количество гостей, занесённых в систему."""
        return self.tourists.count()

    def final_expected_tourists_count(self):
        """Ожидаемое количество гостей, в том числе и не занесённых в систему."""
        # TODO: переписать с использованием trip_money_utils
        contract = self.try_get_client_contract()
        if contract and contract.tourists_count:
            return contract.tourists_count
        return max(self.expected_tourists_count or 1, self.tourists_count())

    def anonymous_tourists_count(self):
        return max(self.final_expected_tourists_count() - self.tourists_count(), 0)

    def commission_estimate(self):
        # TODO: переписать с использованием trip_money_utils
        if not self.supplier:
            return Decimal(0)
        contract = self.try_get_client_contract()
        if not contract:
            return Decimal(0)

        return Supplier.calc_commission(contract.total_price, self.supplier_commission, self.commission_type)

    def commission_paid_amount(self):
        from main.models.money.payment import Payment
        return Payment.get_expenses_sum(self.commission_expense_items, is_outgoing=True)

    def commission_remaining_amount(self):
        return self.commission_estimate() - self.commission_paid_amount()

    def may_change_supplier(self):
        return self.commission_paid_amount() < 1e-6

    def may_clear_draft_flag(self):
        return self.is_draft and self.trip.max_tourists_count >= self.trip.busy_seats_count()

    def arrival_and_departure_str(self):
        trip = self.trip
        tourist = self.tourists.first()
        if not tourist:
            return ''
        return tourist.arrival_and_departure_str(trip)

    def arrival(self):
        first_tourist = self.tourists.first()
        return first_tourist.arrival(self.trip) if first_tourist else None

    def departure(self):
        first_tourist = self.tourists.first()
        return first_tourist.departure(self.trip) if first_tourist else None

    def try_get_inbox_trip_company(self):
        return getattr(self, 'inbox_trip_company', None)

    def try_get_client_contract(self):
        return getattr(self, 'client_contract', None)

    def get_customer(self):
        customer = Client.objects.filter(client_contracts__trip_company=self).first()
        return customer or self.tourists.first()

    def get_default_prepayment(self):
        return self.trip.default_prepayment * (self.expected_tourists_count or 1)

    def has_children_pre7_final(self):
        return self.has_children_pre7 or any([x.date_birth and x.age() <= 7 for x in self.tourists.all()])

    def get_all_roommate_groups(self, hotel_visit):
        # TODO: добавить тесты
        from main.models.trips.accommodation.trip_roommates_group import TripRoommatesGroup
        return TripRoommatesGroup.objects.filter(
            trip_hotel_visit=hotel_visit,
            roommates__trip_companies=self,
        ).distinct()

    def get_single_related_roommate_group(self, hotel_visit):
        return self.get_all_roommate_groups(hotel_visit).first()

    def get_related_draft_companies(self):
        return TripCompany.objects.filter(is_draft=True, tourists__in=self.tourists.all()).exclude(pk=self.pk).distinct()

    def copy_to_trip(self, trip):
        return trip.add_company_with(self.tourists.all(), desired_room_type=self.desired_room_type,
                                     expected_tourists_count=self.expected_tourists_count)

    def may_change_tourists(self):
        contract = self.try_get_client_contract()
        room_type = self.desired_room_type
        return not contract and room_type == self.AccommodationTypeEnum.NONE

    def add_tourist(self, tourist):
        with transaction.atomic():
            if not self.tourists.filter(pk=tourist.pk).exists():
                self.tourists.add(tourist)
            trip = self.trip
            if not trip.tourists.filter(pk=tourist.pk).exists():
                trip.tourists.add(tourist)

    def create_default_partially_filled_contract(self, postfix=""):
        from main.models.trips.tourists.client_contract.client_contract import ClientContract
        first_tourist = self.tourists.first()  # В компании должен быть хотя бы один турист
        surname_letter_1 = first_tourist.surname[0] if first_tourist.surname else ''
        name_letter_1 = first_tourist.name[0]  # Имя не может быть пустым
        contract_number = f"{surname_letter_1}{name_letter_1}{date.today().strftime('%d%m%y')}{postfix}"
        qs = ClientContract.objects.filter(contract_number__startswith=contract_number)
        if qs.count() > 0:
            contract_number = contract_number + '_' + str(qs.count() + 1)
        base_price = self.final_expected_tourists_count() * self.trip.price
        return ClientContract(trip_company=self, contract_number=contract_number, base_price=base_price)

    def add_commission_payment(self, owner, payment_amount, payment_date=None, payer=None, account=None):
        from main.models.money.payment import Payment
        if not self.supplier:
            return None
        with transaction.atomic():
            agency = self.trip.agency
            payer = payer or agency.as_payment_party(save=True)
            supplier_str = truncate_str_custom(self.supplier.any_name, 32)
            trip_str = truncate_str_custom(str(self.trip), 64)
            purpose_text = f"Оплата комиссии контрагенту {supplier_str}, тур {trip_str}"
            client_contract = self.try_get_client_contract()
            if client_contract:
                contract_str = truncate_str_custom(str(client_contract.contract_number), 16)
                purpose_text = purpose_text + f", договор {contract_str}"
            payment = Payment.objects.create(
                agency=agency,
                owner=owner,
                payer=payer,
                account=account,
                payment_date=payment_date if payment_date else date.today(),
                recipient=self.supplier.as_payment_party(save=True),
                is_outgoing=True,
                amount=payment_amount,
                purpose_text=purpose_text,
                trip=self.trip,
            )
            payment.add_supplier_commission_expense_item(self, payment_amount)
            return payment

    @staticmethod
    def default_company_name(main_client, existing_companies):
        from main.utils.utils import get_unique_name
        return get_unique_name(f"{main_client.surname} и Ко", set([x.name for x in existing_companies]))

    @staticmethod
    def remove_from_company(tourist, company):
        company.tourists.remove(tourist)
        if not company.tourists.exists():
            company.delete()

    @staticmethod
    def delete_draft_company(company):
        from main.models.money.supplier_commission_expense_item import SupplierCommissionExpenseItem
        from main.models.money.client_contract_expense_item import ClientContractExpenseItem

        if not company.is_draft:
            return False
        with transaction.atomic():
            for expense_item in SupplierCommissionExpenseItem.objects.filter(trip_company=company):
                expense_item.payment.delete()
            for expense_item in ClientContractExpenseItem.objects.filter(client_contract__trip_company=company):
                expense_item.payment.delete()
            company.tourists.annotate(companies_count=models.Count('trip_companies')).filter(companies_count=1).delete()
            company.delete()
            return True

    class Meta:
        verbose_name = 'Компания туристов'
        verbose_name_plural = 'Компании туристов'
        constraints = [
            UniqueConstraint(fields=['trip', 'name'], name='%(app_label)s_%(class)s_is_unique'),
        ]
