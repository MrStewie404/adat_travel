from django.db import models
from django.db.models import UniqueConstraint

from main.models.routes.route import Route
from main.models.trips.schedule.abstract_trip_day import AbstractTripDay


class RouteDayManager(models.Manager):
    def get_by_natural_key(self, day, *route_args):
        return self.get(day=day, route=Route.objects.get_by_natural_key(*route_args))


class RouteDay(AbstractTripDay):
    """День маршрута."""
    route = models.ForeignKey(Route, on_delete=models.CASCADE, related_name='days')

    objects = RouteDayManager()

    def natural_key(self):
        return (self.day,) + self.route.natural_key()

    natural_key.dependencies = ['main.route']

    def __str__(self):
        return f"{self.route}, {self.day}"

    class Meta:
        verbose_name = 'Маршрут - день'
        verbose_name_plural = 'Маршруты - дни'
        constraints = [
            UniqueConstraint(fields=['route', 'day'], name='%(app_label)s_%(class)s_is_unique'),
        ]
