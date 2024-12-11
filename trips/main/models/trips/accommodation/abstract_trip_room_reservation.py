import abc

from django.db import models

from main.models.abc_model import ABCModel
from main.models.hotels.hotel_pre_booking_and_room import HotelPreBookingAndRoom


class AbstractTripRoomReservationManager(models.Manager, metaclass=abc.ABCMeta):
    def get_by_natural_key(self, room_type__name, *roommates_group_args):
        group = self.roommates_group_class().objects.get_by_natural_key(*roommates_group_args)
        hotel_visit = group.trip_hotel_visit
        hotel = hotel_visit.hotel
        booking_and_room = HotelPreBookingAndRoom.objects.get_by_natural_key(
            hotel_visit.start_date,
            hotel.name,
            hotel.city.name,
            hotel.agency.name if hotel.agency else None,
            room_type__name,
        )
        return self.get(roommates_group=group, hotel_pre_booking_and_room=booking_and_room)

    @staticmethod
    @abc.abstractmethod
    def roommates_group_class():
        pass


class AbstractTripRoomReservation(ABCModel):
    """Бронь номера под группу туристов/работников (для каждого забронированного номера - отдельная запись)."""

    @staticmethod
    def create_roommates_group(group_class, related_name):
        return models.OneToOneField(group_class, on_delete=models.CASCADE, related_name=related_name)

    @property
    @abc.abstractmethod
    def roommates_group(self):
        """Абстрактное поле."""
        pass

    @staticmethod
    def create_hotel_pre_booking_and_room(related_name):
        return models.ForeignKey(HotelPreBookingAndRoom, on_delete=models.CASCADE, related_name=related_name)

    @property
    @abc.abstractmethod
    def hotel_pre_booking_and_room(self):
        """Абстрактное поле."""
        pass

    # Некий номер комнаты, чтобы как-то отличать их
    room_number = models.PositiveSmallIntegerField('Номер комнаты в отеле')

    def __str__(self):
        return f"{self.roommates_group}, {self.hotel_pre_booking_and_room}, {self.room_number}"

    @property
    def room_type(self):
        return self.hotel_pre_booking_and_room.room_type

    def get_caption_str(self):
        hotel_visit = self.roommates_group.trip_hotel_visit
        return self.hotel_pre_booking_and_room.get_room_and_count_str(hotel_visit)

    class Meta:
        abstract = True
