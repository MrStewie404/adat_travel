from django.db import models

from main.models.hotels.hotel_pre_booking import HotelPreBooking
from main.models.money.base_payment_expense_item import BasePaymentExpenseItem
from main.models.trips.accommodation.trip_hotel_visit import TripHotelVisit


class HotelExpenseItem(BasePaymentExpenseItem):
    """Статья платежа - за гостиницу."""
    parent = models.OneToOneField(BasePaymentExpenseItem, on_delete=models.CASCADE, parent_link=True,
                                  related_name='hotel_expense_item')
    hotel_visit = models.ForeignKey(TripHotelVisit, on_delete=models.CASCADE, related_name='payment_expense_items')
    booking = models.ForeignKey(HotelPreBooking, on_delete=models.CASCADE, related_name='payment_expense_items')

    def __str__(self):
        return f"{self.amount} · {self.hotel_visit.trip} · {self.booking}"

    class Meta:
        verbose_name = 'Статья платежа - за гостиницу'
        verbose_name_plural = 'Статьи платежей - за гостиницы'
