from django.core.validators import MinValueValidator
from django.db import models
from django.urls import reverse

from main.models.money.base_payment_expense_item import BasePaymentExpenseItem
from main.utils.utils import format_money


class GuideExtraExpenseItem(BasePaymentExpenseItem):
    """Статья платежа - дополнительные расходы гида."""
    parent = models.OneToOneField(BasePaymentExpenseItem, on_delete=models.CASCADE, parent_link=True,
                                  related_name='guide_extra_expense_item')
    day_number = models.PositiveSmallIntegerField('День тура', blank=True, null=True, validators=[MinValueValidator(1)])

    def __str__(self):
        return f"{self.amount} · День {self.day_number}"

    def short_text_internal(self):
        return f"{self.payment.trip} · День {self.day_number} · {format_money(self.amount)}"

    def details_url_internal(self):
        return reverse('trip_schedule', kwargs={'pk': self.payment.trip.pk})

    class Meta:
        verbose_name = 'Статья платежа - доп. расходы гида'
        verbose_name_plural = 'Статьи платежей - доп. расходы гидов'
