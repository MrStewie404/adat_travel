from django.db import models
from django.urls import reverse

from main.models.money.base_payment_expense_item import BasePaymentExpenseItem
from main.models.trips.tourists.client_contract.client_contract_and_service import ClientContractAndService


class ClientContractServiceExpenseItem(BasePaymentExpenseItem):
    """Статья платежа - за доп. услугу в договоре."""
    parent = models.OneToOneField(BasePaymentExpenseItem, on_delete=models.CASCADE, parent_link=True,
                                  related_name='contract_service_expense_item')
    contract_and_service = models.ForeignKey(ClientContractAndService, on_delete=models.CASCADE,
                                             related_name='payment_expense_items')

    def __str__(self):
        return f"{self.amount} · {self.contract_and_service}"

    def short_text_internal(self):
        return f"{self.contract_and_service.contract.trip} · Услуга {self.contract_and_service.service}"

    def get_contract_internal(self):
        return self.contract_and_service

    def details_url_internal(self):
        return reverse('service_dashboard', kwargs={'pk': self.contract_and_service.service_id})

    class Meta:
        verbose_name = 'Статья платежа - за доп. услугу в договоре'
        verbose_name_plural = 'Статьи платежей - за доп. услуги в договорах'
