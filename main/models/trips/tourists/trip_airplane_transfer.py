from django.db import models

from main.models.trips.tourists.abstract_trip_airplane_transfer import AbstractTripAirplaneTransfer
from main.models.trips.tourists.abstract_trip_transfer import AbstractTripTransfer
from main.models.trips.tourists.trip_and_client import TripAndClient


class TripAirplaneTransferManager(models.Manager):
    def get_by_natural_key(self, transfer_type, *trip_and_client_args):
        return self.get(
            transfer_type=transfer_type,
            trip_and_client=TripAndClient.objects.get_by_natural_key(*trip_and_client_args),
        )


class TripAirplaneTransfer(AbstractTripAirplaneTransfer):
    """Информация о трансфере клиента, прибывающего/улетающего самолётом."""
    objects = TripAirplaneTransferManager()

    def natural_key(self):
        return (self.transfer_type,) + self.trip_and_client.natural_key()

    natural_key.dependencies = ['main.tripandclient']

    class Meta:
        verbose_name = 'Трансфер клиента'
        verbose_name_plural = 'Трансферы клиентов'
        constraints = AbstractTripTransfer.Meta.constraints
