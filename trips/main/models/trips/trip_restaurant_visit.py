from django.db import models
from django.db.models import UniqueConstraint

from main.models.clients.client import Client
from main.models.directory.restaurant import Restaurant
from main.models.trips.trip import Trip


class TripRestaurantVisitManager(models.Manager):
    def get_by_natural_key(self, visit_date, *trip_args):
        return self.get(date=visit_date, trip=Trip.objects.get_by_natural_key(*trip_args))


class TripRestaurantVisit(models.Model):
    """Посещение ресторана в конкретную поездку."""
    trip = models.ForeignKey(Trip, on_delete=models.CASCADE, related_name='trip_restaurant_visits')
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name='trip_restaurant_visits')
    tourists = models.ManyToManyField(Client, through='MealOrder', related_name='trip_restaurant_visits', blank=True)
    date = models.DateField('Дата')
    guide_contacts = models.CharField('Контакты гида', max_length=256)
    comment = models.TextField('Комментарий', blank=True)

    objects = TripRestaurantVisitManager()

    def natural_key(self):
        return (self.date,) + self.trip.natural_key()

    natural_key.dependencies = ['main.trip']

    def __str__(self):
        return f"{self.trip}, {self.restaurant}, {self.date}"

    class Meta:
        verbose_name = 'Ресторан - визит'
        verbose_name_plural = 'Рестораны - визиты'
        constraints = [
            UniqueConstraint(fields=['trip', 'restaurant', 'date'], name='%(app_label)s_%(class)s_is_unique'),
        ]
