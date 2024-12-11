from django.db import models
from django.db.models import UniqueConstraint

from main.models.clients.client import Client
from main.models.trips.trip import Trip


class TripAndClientManager(models.Manager):
    def get_by_natural_key(self, trip__name, trip__start_date, trip__agency, *client_args):
        return self.get(
            trip=Trip.objects.get_by_natural_key(trip__name, trip__start_date, trip__agency),
            client=Client.objects.get_by_natural_key(*client_args),
        )


class TripAndClient(models.Model):
    """Связь "туры - клиенты"."""
    trip = models.ForeignKey(Trip, on_delete=models.CASCADE)
    client = models.ForeignKey(Client, on_delete=models.CASCADE)

    objects = TripAndClientManager()

    def natural_key(self):
        return self.trip.natural_key() + self.client.natural_key()

    natural_key.dependencies = ['main.trip', 'main.client']

    def __str__(self):
        return f"{self.trip}, {self.client}"

    def arrival(self):
        from main.models.trips.tourists.abstract_trip_transfer import AbstractTripTransfer
        return self.transfers.filter(transfer_type=AbstractTripTransfer.TransferTypeEnum.ARRIVAL).first()

    def departure(self):
        from main.models.trips.tourists.abstract_trip_transfer import AbstractTripTransfer
        return self.transfers.filter(transfer_type=AbstractTripTransfer.TransferTypeEnum.DEPARTURE).first()

    class Meta:
        verbose_name = 'Тур - клиент'
        verbose_name_plural = 'Туры - клиенты'
        constraints = [
            UniqueConstraint(fields=['trip', 'client'], name='%(app_label)s_%(class)s_is_unique'),
        ]
