from django.db import models
from django.urls import reverse

from main.models.money.base_payment_expense_item import BasePaymentExpenseItem
from main.models.trips.tourists.client_contract.client_contract import ClientContract
from main.utils.utils import format_money


class ClientContractExpenseItem(BasePaymentExpenseItem):
    """Статья платежа - за туристический договор."""
    parent = models.OneToOneField(BasePaymentExpenseItem, on_delete=models.CASCADE, parent_link=True,
                                  related_name='contract_expense_item')
    client_contract = models.ForeignKey(ClientContract, on_delete=models.CASCADE,
                                        related_name='payment_expense_items')

    def __str__(self):
        return f"{self.amount} · {self.client_contract}"

    def short_text_internal(self):
        return f"{self.client_contract.trip} · Договор {self.client_contract.contract_number} · {format_money(self.amount)}"

    def details_url_internal(self):
        return reverse('client_contract_dashboard', kwargs={'company_pk': self.client_contract.trip_company_id})

    def get_contract_internal(self):
        return self.client_contract

    @property
    def url_name(self):
        return 'client_contract_dashboard'

    @property
    def url_args(self):
        return [self.client_contract.trip_company_id]

    class Meta:
        verbose_name = 'Статья платежа - за туристический договор'
        verbose_name_plural = 'Статьи платежей - за туристические договоры'
