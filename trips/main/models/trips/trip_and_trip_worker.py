from django.db import models
from django.db.models import UniqueConstraint

from main.models.trips.trip import Trip
from main.models.workers.trip_worker import TripWorker


class TripAndTripWorkerManager(models.Manager):
    def get_by_natural_key(self, trip__name, trip__start_date, trip__agency, *worker_args):
        return self.get(
            trip=Trip.objects.get_by_natural_key(trip__name, trip__start_date, trip__agency),
            worker=TripWorker.objects.get_by_natural_key(*worker_args),
        )


class TripAndTripWorker(models.Model):
    """Связь "туры - персонал"."""
    trip = models.ForeignKey(Trip, on_delete=models.CASCADE)
    worker = models.ForeignKey(TripWorker, on_delete=models.CASCADE)

    objects = TripAndTripWorkerManager()

    def natural_key(self):
        return self.trip.natural_key() + self.worker.natural_key()

    natural_key.dependencies = ['main.trip', 'main.tripworker']

    def __str__(self):
        return f"{self.trip}, {self.worker}"

    class Meta:
        verbose_name = 'Тур - персонал'
        verbose_name_plural = 'Туры - персонал'
        constraints = [
            UniqueConstraint(fields=['trip', 'worker'], name='%(app_label)s_%(class)s_is_unique'),
        ]
