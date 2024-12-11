from django.db import models
from django.db.models import UniqueConstraint

from main.models.agency.agency import Agency
from main.models.custom_unique_error_mixin import CustomUniqueErrorMixin
from main.models.directory.city import City


class HotelManager(models.Manager):
    def get_by_natural_key(self, name, agency__name, *city_args):
        return self.get(
            name=name,
            agency=Agency.objects.get_by_natural_key(agency__name) if agency__name else None,
            city=City.objects.get_by_natural_key(*city_args),
        )


class Hotel(CustomUniqueErrorMixin, models.Model):
    agency = models.ForeignKey(Agency, on_delete=models.CASCADE, related_name='hotels', blank=True, null=True)
    city = models.ForeignKey(City, on_delete=models.CASCADE, related_name='hotels')
    name = models.CharField('Название', max_length=64)
    address = models.CharField('Адрес', max_length=256, blank=True)
    phone_number = models.CharField('Телефон', max_length=32, blank=True)
    email = models.EmailField('E-mail', blank=True)
    website = models.URLField('Официальный сайт', blank=True)
    lat = models.FloatField('Широта', blank=True, null=True)
    lon = models.FloatField('Долгота', blank=True, null=True)
    room_facilities = models.TextField('Что есть в номерах', blank=True)
    comment = models.TextField('Комментарий', blank=True)

    objects = HotelManager()

    def natural_key(self):
        agency_key = self.agency.natural_key() if self.agency else (None,)
        return (self.name,) + agency_key + self.city.natural_key()

    natural_key.dependencies = ['main.agency', 'main.city']

    def __str__(self):
        return f"{self.city.name} · {self.name}"

    def str_for_booking(self):
        return f"{self.name} · {self.city.name}"

    def may_delete(self):
        return not self.trips.exists() and \
               not self.trip_hotel_visits.exists() and \
               not self.pre_bookings.exists() and \
               all(x.may_delete() for x in self.room_types.all())

    def get_unique_together_error_message(self):
        return "Гостиница с таким названием уже существует в этом городе."

    @staticmethod
    def get_ordered_hotels(agency, preferred_city):
        hotels = Hotel.objects.filter(models.Q(agency=agency) | models.Q(agency__isnull=True))
        if preferred_city:
            hotels = hotels.extra(select={"is_same_city": f"city_id='{preferred_city.pk}'"}). \
                order_by('-is_same_city', 'city__name', 'name')
        else:
            hotels = hotels.order_by('city__name', 'name')
        return hotels

    class Meta:
        verbose_name = 'Гостиница'
        verbose_name_plural = 'Гостиницы'
        constraints = [
            UniqueConstraint(fields=['agency', 'city', 'name'], name='%(app_label)s_%(class)s_name_is_unique'),
        ]
        permissions = [
            ('manage_hotels', 'Пользователь может управлять гостиницами, но не удалять их (#наше)'),
            ('delete_hotels', 'Пользователь может удалять гостиницы (#наше)'),
            ('manage_hotel_bookings', 'Пользователь может управлять бронированиями гостиниц (#наше)'),
        ]
