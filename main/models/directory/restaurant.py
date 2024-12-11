from django.db import models
from django.db.models import UniqueConstraint

from main.models.agency.agency import Agency
from main.models.custom_unique_error_mixin import CustomUniqueErrorMixin
from main.models.directory.city import City


class RestaurantManager(models.Manager):
    def get_by_natural_key(self, name):
        return self.get(name=name)


class Restaurant(CustomUniqueErrorMixin, models.Model):
    agency = models.ForeignKey(Agency, on_delete=models.CASCADE, related_name='restaurants', blank=True, null=True)
    city = models.ForeignKey(City, on_delete=models.CASCADE, related_name='restaurants')
    name = models.CharField('Название', max_length=64)
    address = models.CharField('Адрес', max_length=256, blank=True)
    phone_number = models.CharField('Телефон', max_length=32, blank=True)
    email = models.EmailField('E-mail', blank=True)
    website = models.URLField('Официальный сайт', blank=True)
    lat = models.FloatField('Широта', blank=True, null=True)
    lon = models.FloatField('Долгота', blank=True, null=True)
    comment = models.TextField('Комментарий', blank=True)

    objects = RestaurantManager()

    def natural_key(self):
        return (self.name,)

    def __str__(self):
        return f"{self.name} ({self.city.name})"

    def get_unique_together_error_message(self):
        return "Ресторан с таким названием уже существует в этом городе."

    class Meta:
        verbose_name = 'Ресторан'
        verbose_name_plural = 'Рестораны'
        constraints = [
            UniqueConstraint(fields=['agency', 'city', 'name'], name='%(app_label)s_%(class)s_name_is_unique'),
        ]
        permissions = [
            ('manage_restaurants', 'Пользователь может управлять ресторанами, но не удалять их (#наше)'),
            ('delete_restaurants', 'Пользователь может удалять рестораны (#наше)'),
        ]
