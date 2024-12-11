from django.db import models
from django.db.models import UniqueConstraint

from main.models.directory.city import City
from main.models.routes.route import Route
from main.models.trips.schedule.abstract_trip_and_city import AbstractTripAndCity


class RouteAndCityManager(models.Manager):
    def get_by_natural_key(self, day, objective, route__name, route__agency, *city_args):
        return self.get(
            day=day,
            objective=objective,
            route=Route.objects.get_by_natural_key(route__name, route__agency),
            city=City.objects.get_by_natural_key(*city_args),
        )


class RouteAndCity(AbstractTripAndCity):
    """Город проживания/посещения на маршруте."""
    route = models.ForeignKey(Route, on_delete=models.CASCADE)

    objects = RouteAndCityManager()

    def natural_key(self):
        return (self.day, self.objective) + self.route.natural_key() + self.city.natural_key()

    natural_key.dependencies = ['main.route', 'main.city']

    def __str__(self):
        return f"{self.route}, {self.day}, {self.city}"

    class Meta:
        verbose_name = 'Маршрут - город'
        verbose_name_plural = 'Маршруты - города'
        constraints = [
            UniqueConstraint(fields=['route', 'city', 'day', 'objective'], name='%(app_label)s_%(class)s_is_unique'),
        ]
