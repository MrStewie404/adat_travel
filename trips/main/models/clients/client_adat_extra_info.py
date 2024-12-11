from django.db import models
from django.db.models import UniqueConstraint

from main.models.clients.client import Client


class ClientAdatExtraInfo(models.Model):
    """Дополнительная информация, импортированная из БД АДАТ."""
    person = models.OneToOneField(Client, on_delete=models.CASCADE, related_name='adat_extra_info')
    adat_id = models.BigIntegerField('ID')
    company_name = models.CharField('Компания', max_length=128, blank=True)
    source = models.CharField('Источник', max_length=128, blank=True)
    source_additional_info = models.CharField('Дополнительно об источнике', max_length=256, blank=True)
    preferred_communication_channel = models.CharField('Предпочтительный канал связи', max_length=256, blank=True)
    tourists_count = models.PositiveSmallIntegerField('Количество гостей', blank=True, null=True)
    city = models.CharField('Город', max_length=32, blank=True)

    class Meta:
        verbose_name = 'Дополнительная информация из БД АДАТ'
        verbose_name_plural = 'Дополнительная информация из БД АДАТ'
        constraints = [
            UniqueConstraint(fields=['adat_id'], name='%(app_label)s_%(class)s_is_unique'),
        ]
