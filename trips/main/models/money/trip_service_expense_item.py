from django.db import models
from django.urls import reverse

from main.models.money.base_payment_expense_item import BasePaymentExpenseItem
from main.models.trips.schedule.trip_and_service import TripAndService


class TripServiceExpenseItem(BasePaymentExpenseItem):
    """Статья платежа - за услугу в туре."""
    parent = models.OneToOneField(BasePaymentExpenseItem, on_delete=models.CASCADE, parent_link=True,
                                  related_name='trip_service_expense_item')
    trip_and_service = models.ForeignKey(TripAndService, on_delete=models.CASCADE,
                                         related_name='payment_expense_items')

    def __str__(self):
        return f"{self.amount} · {self.trip_and_service}"

    def short_text_internal(self):
        return f"{self.trip_and_service.trip} · Услуга {self.trip_and_service.service.name}"

    def details_url_internal(self):
        return reverse('service_dashboard', kwargs={'pk': self.trip_and_service.service_id})

    class Meta:
        verbose_name = 'Статья платежа - за услугу в туре'
        verbose_name_plural = 'Статьи платежей - за услуги в турах'
