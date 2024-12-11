from django.db import models
from django.db.models import UniqueConstraint

from main.models.clients.client import Client
from main.models.trips.trip_restaurant_visit import TripRestaurantVisit


class MealOrder(models.Model):
    """Предзаказ блюд клиентом."""
    restaurant_visit = models.ForeignKey(TripRestaurantVisit, on_delete=models.CASCADE, related_name='meal_orders')
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='meal_orders')
    meal_preferences = models.CharField('Заказ блюд', max_length=256)

    def __str__(self):
        return f"{self.restaurant_visit}, {self.client}"

    class Meta:
        verbose_name = 'Заказ блюд'
        verbose_name_plural = 'Заказы блюд'
        constraints = [
            UniqueConstraint(fields=['restaurant_visit', 'client'], name='%(app_label)s_%(class)s_is_unique'),
        ]
