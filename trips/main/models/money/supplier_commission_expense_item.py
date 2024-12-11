from django.db import models
from django.urls import reverse

from main.models.money.base_payment_expense_item import BasePaymentExpenseItem
from main.models.services.supplier import Supplier
from main.models.trips.tourists.trip_company import TripCompany
from main.utils.utils import format_money


class SupplierCommissionExpenseItem(BasePaymentExpenseItem):
    """Статья платежа - комиссия контрагенту."""
    parent = models.OneToOneField(BasePaymentExpenseItem, on_delete=models.CASCADE, parent_link=True,
                                  related_name='supplier_commission_expense_item')
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE,
                                 related_name='commission_expense_items')
    trip_company = models.ForeignKey(TripCompany, on_delete=models.CASCADE,
                                     related_name='commission_expense_items')

    def __str__(self):
        return f"{self.amount} · {self.supplier} · {self.trip_company}"

    def short_text_internal(self):
        return f"{self.trip_company.trip} · Контрагент {self.supplier} · {format_money(self.amount)}"

    def details_url_internal(self):
        return reverse('client_contract_dashboard', kwargs={'company_pk': self.trip_company.pk})

    class Meta:
        verbose_name = 'Статья платежа - комиссия контрагенту'
        verbose_name_plural = 'Статьи платежей - комиссии контрагентам'
