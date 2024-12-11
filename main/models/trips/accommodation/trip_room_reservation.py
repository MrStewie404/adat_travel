from main.models.trips.accommodation.abstract_trip_room_reservation import AbstractTripRoomReservationManager, \
    AbstractTripRoomReservation
from main.models.trips.accommodation.trip_roommates_group import TripRoommatesGroup


class TripRoomReservationManager(AbstractTripRoomReservationManager):
    @staticmethod
    def roommates_group_class():
        return TripRoommatesGroup


class TripRoomReservation(AbstractTripRoomReservation):
    """Бронь номера под группу туристов (для каждого забронированного номера - отдельная запись)."""
    roommates_group = AbstractTripRoomReservation.create_roommates_group(group_class=TripRoommatesGroup,
                                                                         related_name='room_reservation')
    hotel_pre_booking_and_room = AbstractTripRoomReservation. \
        create_hotel_pre_booking_and_room(related_name='tourist_room_reservations')

    objects = TripRoomReservationManager()

    def natural_key(self):
        return (self.hotel_pre_booking_and_room.room_type.name,) + self.roommates_group.natural_key()

    natural_key.dependencies = ['main.triproommatesgroup', 'main.hotelprebookingandroom']

    class Meta:
        verbose_name = 'Бронь номера для группы туристов'
        verbose_name_plural = 'Брони номеров для групп туристов'
