from django.db import models

from main.models.trips.tourists.abstract_trip_transfer import AbstractTripTransfer


class AbstractTripAirplaneTransfer(AbstractTripTransfer):
    """Абстрактная модель: информация о трансфере клиента, прибывающего/улетающего самолётом."""
    flight_number = models.CharField('Номер рейса', max_length=32, blank=True)

    def __str__(self):
        return f"{self.trip_and_client}, {self.transfer_type}, {self.date_time_local.strftime('%d.%m.%y %H:%M')}, " \
               f"{self.flight_number}"

    class Meta:
        abstract = True
