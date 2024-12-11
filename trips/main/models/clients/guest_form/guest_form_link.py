from django.db import models
from django.utils import timezone
from django.utils.crypto import get_random_string

from main.models.trips.tourists.trip_company import TripCompany
from main.models.utils import get_unique_token


class GuestFormLink(models.Model):
    """Ссылка на анкету гостя (гостей)."""
    trip_company = models.OneToOneField(TripCompany, on_delete=models.CASCADE, related_name='guest_form_link')
    token = models.CharField('Токен', max_length=16, unique=True)
    guest_count = models.PositiveSmallIntegerField('Количество гостей')
    created_at = models.DateTimeField('Дата создания', default=timezone.now)

    def __str__(self):
        return f"{self.trip_company}: ссылка на анкету гостя (гостей)"

    @staticmethod
    def get_unique_token():
        return get_unique_token(GuestFormLink, 'token')

    class Meta:
        verbose_name = 'Ссылка на анкету гостя (гостей)'
        verbose_name_plural = 'Ссылки на анкеты гостей'
