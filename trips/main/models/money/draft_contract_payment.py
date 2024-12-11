from django.db import models
from django.utils import timezone

from main.models.money.agency_payment_token import AgencyPaymentToken
from main.models.trips.tourists.client_contract.client_contract import ClientContract
from main.models.utils import create_price_field


class DraftContractPayment(models.Model):
    """Неподтверждённый платёж."""
    payment_token = models.ForeignKey(AgencyPaymentToken, on_delete=models.CASCADE, related_name='draft_payments')
    client_contract = models.ForeignKey(ClientContract, on_delete=models.CASCADE, related_name='draft_payments')
    payment_id = models.CharField('Идентификатор платежа', max_length=128)
    created_at = models.DateTimeField('Дата создания', default=timezone.now)
    amount = create_price_field('Сумма')

    def __str__(self):
        return f"{self.client_contract} - {self.amount}"

    class Meta:
        verbose_name = 'Неподтверждённый платёж'
        verbose_name_plural = 'Неподтверждённые платежи'
