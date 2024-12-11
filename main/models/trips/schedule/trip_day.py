from django.db import models
from django.db.models import UniqueConstraint

from main.models.trips.schedule.abstract_trip_day import AbstractTripDay
from main.models.trips.trip import Trip


class TripDayManager(models.Manager):
    def get_by_natural_key(self, day, *trip_args):
        return self.get(day=day, trip=Trip.objects.get_by_natural_key(*trip_args))


class TripDay(AbstractTripDay):
    """День тура."""
    trip = models.ForeignKey(Trip, on_delete=models.CASCADE, related_name='days')

    objects = TripDayManager()

    def natural_key(self):
        return (self.day,) + self.trip.natural_key()

    natural_key.dependencies = ['main.trip']

    def __str__(self):
        return f"{self.trip}, {self.date}"

    @property
    def date(self):
        return self.trip.get_date(self.day)

    class Meta:
        verbose_name = 'Тур - день'
        verbose_name_plural = 'Туры - дни'
        constraints = [
            UniqueConstraint(fields=['trip', 'day'], name='%(app_label)s_%(class)s_is_unique'),
        ]
