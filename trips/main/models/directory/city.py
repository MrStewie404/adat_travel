from django.db import models
from django.db.models import UniqueConstraint

from main.models.agency.agency import Agency
from main.models.custom_unique_error_mixin import CustomUniqueErrorMixin


class CityManager(models.Manager):
    def get_by_natural_key(self, name, agency__name):
        return self.get(name=name, agency=Agency.objects.get_by_natural_key(agency__name) if agency__name else None)


class City(CustomUniqueErrorMixin, models.Model):
    agency = models.ForeignKey(Agency, on_delete=models.CASCADE, related_name='cities', blank=True, null=True)
    name = models.CharField('Название города', max_length=64)
    region = models.CharField('Регион', max_length=64, blank=True)
    country = models.CharField('Страна', max_length=64)
    lat = models.FloatField('Широта', blank=True, null=True)
    lon = models.FloatField('Долгота', blank=True, null=True)

    objects = CityManager()

    def natural_key(self):
        # Регион и страну пока игнорируем
        agency_key = self.agency.natural_key() if self.agency else (None,)
        return (self.name,) + agency_key

    natural_key.dependencies = ['main.agency']

    def __str__(self):
        return self.name

    def may_delete(self):
        return not self.hotels.exists() and not self.restaurants.exists() and not self.services.exists()

    def get_unique_together_error_message(self):
        return "Город с таким названием уже существует."

    class Meta:
        verbose_name = 'Город'
        verbose_name_plural = 'Города'
        constraints = [
            UniqueConstraint(fields=['agency', 'name', 'region', 'country'],
                             name='%(app_label)s_%(class)s_name_is_unique'),
        ]
        permissions = [
            ('manage_cities', 'Пользователь может управлять городами, но не удалять их (#наше)'),
            ('delete_cities', 'Пользователь может удалять города (#наше)'),
        ]
