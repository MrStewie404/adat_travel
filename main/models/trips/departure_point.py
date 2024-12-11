from django.db import models
from django.db.models import UniqueConstraint

from main.models.agency.agency import Agency


class DeparturePoint(models.Model):
    """Пункт отправления."""
    agency = models.ForeignKey(Agency, on_delete=models.CASCADE, related_name='departure_points')
    departure_city = models.CharField('Выезд из', max_length=32)
    departure_address = models.CharField('Место сбора', max_length=128)
    lat = models.DecimalField('Широта', max_digits=9, decimal_places=6, blank=True, null=True)
    lon = models.DecimalField('Долгота', max_digits=9, decimal_places=6, blank=True, null=True)

    def __str__(self):
        return f"Выезд из {self.departure_city}, место сбора - {self.departure_address}"

    class Meta:
        verbose_name = 'Место сбора группы'
        verbose_name_plural = 'Места сбора групп'
        constraints = [
            UniqueConstraint(fields=['agency', 'departure_city', 'departure_address'],
                             name='%(app_label)s_%(class)s_name_is_unique'),
        ]
