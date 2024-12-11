from django.db import models
from django.db.models import UniqueConstraint

from main.models.routes.route import Route
from main.models.services.service import Service
from main.models.trips.schedule.abstract_trip_and_service import AbstractTripAndService


class RouteAndServiceManager(models.Manager):
    def get_by_natural_key(self, day, route__name, route__agency, *service_args):
        return self.get(
            day=day,
            route=Route.objects.get_by_natural_key(route__name, route__agency),
            service=Service.objects.get_by_natural_key(*service_args),
        )


class RouteAndService(AbstractTripAndService):
    """Связь "маршруты - услуги"."""
    route = models.ForeignKey(Route, on_delete=models.CASCADE)

    objects = RouteAndServiceManager()

    def natural_key(self):
        return (self.day,) + self.route.natural_key() + self.service.natural_key()

    natural_key.dependencies = ['main.route', 'main.service']

    def __str__(self):
        return f"{self.route}, {self.day}, {self.service}"

    class Meta(AbstractTripAndService.Meta):
        verbose_name = 'Маршрут - услуга'
        verbose_name_plural = 'Маршруты - услуги'
        constraints = [
            UniqueConstraint(fields=['route', 'service', 'day'], name='%(app_label)s_%(class)s_is_unique'),
        ]
