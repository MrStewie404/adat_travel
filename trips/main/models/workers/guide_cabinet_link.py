from django.db import models
from django.utils import timezone
from django.utils.crypto import get_random_string

from main.models.utils import get_unique_token
from main.models.workers.trip_worker import TripWorker


class GuideCabinetLink(models.Model):
    """Ссылка на личный кабинет гида."""
    worker = models.OneToOneField(TripWorker, on_delete=models.CASCADE, related_name='guide_cabinet_link')
    short_cabinet_id = models.CharField('Ссылка - ID кабинета', max_length=16, unique=True)
    created_at = models.DateTimeField('Дата создания', default=timezone.now)

    def __str__(self):
        return f"{self.worker}: ссылка на личный кабинет"

    @staticmethod
    def get_unique_cabinet_id():
        return get_unique_token(GuideCabinetLink, 'short_cabinet_id')

    class Meta:
        verbose_name = 'Ссылка на личный кабинет гида'
        verbose_name_plural = 'Ссылки на личные кабинеты гидов'
