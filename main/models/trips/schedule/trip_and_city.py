from django.db import models
from django.db.models import UniqueConstraint

from main.models.directory.city import City
from main.models.trips.schedule.abstract_trip_and_city import AbstractTripAndCity
from main.models.trips.trip import Trip


class TripAndCityManager(models.Manager):
    def get_by_natural_key(self, day, objective, trip__name, trip__start_date, trip__agency, *city_args):
        return self.get(
            day=day, objective=objective,
            trip=Trip.objects.get_by_natural_key(trip__name, trip__start_date, trip__agency),
            city=City.objects.get_by_natural_key(*city_args),
        )


class TripAndCity(AbstractTripAndCity):
    """Город ночёвки/посещения."""
    trip = models.ForeignKey(Trip, on_delete=models.CASCADE)

    objects = TripAndCityManager()

    def natural_key(self):
        return (self.day, self.objective) + self.trip.natural_key() + self.city.natural_key()

    natural_key.dependencies = ['main.trip', 'main.city']

    def __str__(self):
        return f"{self.trip}, {self.date}, {self.city}"

    @property
    def date(self):
        return self.trip.get_date(self.day)

    class Meta:
        verbose_name = 'Тур - город'
        verbose_name_plural = 'Туры - города'
        constraints = [
            UniqueConstraint(fields=['trip', 'city', 'day', 'objective'], name='%(app_label)s_%(class)s_is_unique'),
        ]
