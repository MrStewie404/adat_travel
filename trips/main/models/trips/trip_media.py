from django.db import models
from django.db.models import UniqueConstraint

from main.models.abstract_media import AbstractMedia
from main.models.trips.trip import Trip


class TripMedia(AbstractMedia):
    """Файл, прикреплённый к туру пользователем."""
    trip = models.ForeignKey(Trip, on_delete=models.CASCADE, related_name='trip_media_files')

    def __str__(self):
        return f"{self.trip}, {self.file.name}, {self.description}"

    @property
    def agency(self):
        return self.trip.agency

    class Meta:
        verbose_name = 'Медиафайл в туре'
        verbose_name_plural = 'Медиафайлы в турах'
        constraints = [
            UniqueConstraint(fields=['trip', 'file'], name='%(app_label)s_%(class)s_is_unique'),
        ]
