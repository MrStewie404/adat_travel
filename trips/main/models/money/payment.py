from collections import OrderedDict
from datetime import date
from decimal import Decimal

from django.db import models
from django.db.models.functions import Coalesce
from django.utils import timezone

from main.models.agency.agency import Agency
from main.models.agency.agency_employee import AgencyEmployee
from main.models.money.base_money_account import BaseMoneyAccount
from main.models.money.base_payment_party import BasePaymentParty
from main.models.trips.trip import Trip
from main.models.utils import create_price_field
from main.utils.utils import format_money


class Payment(models.Model):
    """Входящий или исходящий платёж."""
    agency = models.ForeignKey(Agency, on_delete=models.CASCADE, related_name='payments')
    account = models.ForeignKey(BaseMoneyAccount, on_delete=models.PROTECT, related_name='payments', null=True, blank=True)
    owner = models.ForeignKey(AgencyEmployee, on_delete=models.SET_NULL, blank=True, null=True,
                              related_name='created_payments')
    created_at = models.DateTimeField('Дата создания', default=timezone.now)
    payment_date = models.DateField('Дата платежа', default=date.today)
    payer = models.ForeignKey(BasePaymentParty, on_delete=models.CASCADE, related_name='output_payments')
    recipient = models.ForeignKey(BasePaymentParty, on_delete=models.CASCADE, related_name='input_payments',
                                  blank=True, null=True)
    is_outgoing = models.BooleanField('Исходящий платёж', default=False)
    amount = create_price_field('Сумма')
    purpose_text = models.CharField('Назначение (текст)', max_length=256)
    comment = models.CharField('Дополнительный комментарий', max_length=256, blank=True)
    trip = models.ForeignKey(Trip, on_delete=models.SET_NULL, blank=True, null=True, related_name='trip_payments')

    def __str__(self):
        return f"{self.payment_date} - {self.trip} - {self.purpose_text} - {self.amount}"

    @property
    def amount_sum(self):
        if self.is_outgoing:
            return self.amount * -1
        return self.amount

    @property
    def amount_sum_str(self):
        return format_money(self.amount_sum, show_r_sign=True)

    @property
    def date_of_payment(self):
        return self.payment_date.strftime('%d.%m.%y')

    @property
    def datetime_of_creation(self):
        # См. CustomTimezoneMiddleware - там мы задаём текущим московское время
        local_date_time = timezone.localtime(self.created_at)
        return local_date_time.strftime('%d.%m.%Y %H:%M')

    @property
    def payer_name(self):
        return self.payer.name if self.payer else "не задан"

    @property
    def recipient_name(self):
        return self.recipient.name if self.recipient else "не задан"

    @property
    def owner_name(self):
        return str(self.owner) if self.owner else "не задан"

    @property
    def trips_with_contracts(self):
        contracts_by_trip = OrderedDict()
        for ex_item in self.expense_items.all():
            contract = ex_item.get_contract
            if contract:
                contracts_by_trip[contract.trip] = [contract]

        if not contracts_by_trip and self.trip:
            contracts_by_trip[self.trip] = []

        return contracts_by_trip.items()

    @property
    def dashboard_page_title(self):
        return f"Платёж от {self.date_of_payment} назначение \"{self.purpose_text}\""

    @property
    def label_for_form(self):
        return f"{self.date_of_payment} · {self.amount_sum_str} · {self.payer}"

    @staticmethod
    def get_expenses_sum(expense_items_queryset, is_outgoing):
        qs = expense_items_queryset.filter(payment__is_outgoing=is_outgoing)
        return qs.aggregate(amount_sum=Coalesce(models.Sum('amount'), Decimal(0)))['amount_sum'] or Decimal(0)

    @property
    def get_account_description(self):
        return self.account.short_text if self.account else ''

    @property
    def get_prefetched_expenses_description(self):
        texts_list = []
        for item in self.expense_items_list_q:
            # Тут вызываем метод short_text_internal, чтобы для дочернего элемента не вызывался метод
            # child_expense_item_or_self, который требует дополнительных обращений к БД
            texts_list.append(item.child_expense_item_or_self.short_text_internal())
        return "\n".join(texts_list)

    @property
    def media(self):
        if self.payment_media_files.count():
            return self.payment_media_files.all()[0]

        return None

    @staticmethod
    def get_expense_item_for_guide(expense_items_queryset, agency, is_outgoing):
        return Payment.filter_expense_items_for_guide(expense_items_queryset, agency, is_outgoing).first()

    @staticmethod
    def filter_expense_items_for_guide(expense_items_queryset, agency, is_outgoing):
        from main.models.workers.trip_worker import TripWorker
        from main.models.money.person_payment_party import PersonPaymentParty
        trip_worker_pks = [x.pk for x in TripWorker.objects.filter(agency=agency)]
        trip_worker_party_pks = [x.pk for x in PersonPaymentParty.objects.filter(person__in=trip_worker_pks)]
        return expense_items_queryset.filter(payment__payer__in=trip_worker_party_pks, payment__is_outgoing=is_outgoing)

    @staticmethod
    def filter_expense_items_not_for_guide(expense_items_queryset, agency, is_outgoing):
        from main.models.workers.trip_worker import TripWorker
        from main.models.money.person_payment_party import PersonPaymentParty
        trip_worker_pks = [x.pk for x in TripWorker.objects.filter(agency=agency)]
        trip_worker_party_pks = [x.pk for x in PersonPaymentParty.objects.filter(person__in=trip_worker_pks)]
        return expense_items_queryset.filter(payment__is_outgoing=is_outgoing).\
            exclude(payment__payer__in=trip_worker_party_pks)

    @staticmethod
    def filter_by_trip_expense_items(query_set, trip_pk):
        from main.models.money.client_contract_expense_item import ClientContractExpenseItem
        from main.models.money.trip_service_expense_item import TripServiceExpenseItem
        from main.models.money.hotel_expense_item import HotelExpenseItem
        from main.models.money.client_contract_service_expense_item import ClientContractServiceExpenseItem
        from main.models.money.guide_extra_expense_item import GuideExtraExpenseItem
        cc = ClientContractExpenseItem.objects.filter(client_contract__trip_company__trip_id=trip_pk)
        te = TripServiceExpenseItem.objects.filter(trip_and_service__trip_id=trip_pk)
        he = HotelExpenseItem.objects.filter(hotel_visit__trip_id=trip_pk)
        cce = ClientContractServiceExpenseItem.objects.filter(contract_and_service__trip_and_service__trip_id=trip_pk)
        ge = GuideExtraExpenseItem.objects.filter(payment__trip_id=trip_pk)
        query_set = query_set.filter(expense_items__in=te) | \
                    query_set.filter(expense_items__in=cc) | \
                    query_set.filter(expense_items__in=he) | \
                    query_set.filter(expense_items__in=cce) | \
                    query_set.filter(expense_items__in=ge) | \
                    query_set.filter(trip_id=trip_pk)
        return query_set.distinct()

    def add_client_contract_expense_item(self, contract, amount):
        from main.models.money.client_contract_expense_item import ClientContractExpenseItem
        return ClientContractExpenseItem.objects.create(
            payment=self,
            amount=amount,
            client_contract=contract,
        )

    def add_supplier_commission_expense_item(self, trip_company, amount):
        from main.models.money.supplier_commission_expense_item import SupplierCommissionExpenseItem
        return SupplierCommissionExpenseItem.objects.create(
            payment=self,
            amount=amount,
            trip_company=trip_company,
            supplier=trip_company.supplier,
        )

    class Meta:
        verbose_name = 'Платёж'
        verbose_name_plural = 'Платежи'
