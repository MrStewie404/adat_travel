from django.db import models
from django.db.models import UniqueConstraint

from main.models.abstract_media import AbstractMedia
from main.models.services.service import Service


class ServiceMedia(AbstractMedia):
    """Файл, прикреплённый к услуге пользователем."""
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name='media_files')

    def __str__(self):
        return f"{self.service}, {self.file.name}, {self.description}"

    @property
    def agency(self):
        return self.service.agency

    class Meta:
        verbose_name = 'Медиафайл в услуге'
        verbose_name_plural = 'Медиафайлы в услугах'
        constraints = [
            UniqueConstraint(fields=['service', 'file'], name='%(app_label)s_%(class)s_is_unique'),
        ]
