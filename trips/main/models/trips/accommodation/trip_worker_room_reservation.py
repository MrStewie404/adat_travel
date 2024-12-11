from main.models.trips.accommodation.abstract_trip_room_reservation import AbstractTripRoomReservationManager, \
    AbstractTripRoomReservation
from main.models.trips.accommodation.trip_worker_roommates_group import TripWorkerRoommatesGroup


class TripWorkerRoomReservationManager(AbstractTripRoomReservationManager):
    @staticmethod
    def roommates_group_class():
        return TripWorkerRoommatesGroup


class TripWorkerRoomReservation(AbstractTripRoomReservation):
    """Бронь номера под группу работников (для каждого забронированного номера - отдельная запись)."""
    roommates_group = AbstractTripRoomReservation.create_roommates_group(group_class=TripWorkerRoommatesGroup,
                                                                         related_name='room_reservation')
    hotel_pre_booking_and_room = AbstractTripRoomReservation. \
        create_hotel_pre_booking_and_room(related_name='trip_worker_room_reservations')

    objects = TripWorkerRoomReservationManager()

    def natural_key(self):
        return (self.hotel_pre_booking_and_room.room_type.name,) + self.roommates_group.natural_key()

    natural_key.dependencies = ['main.tripworkerroommatesgroup', 'main.hotelprebookingandroom']

    class Meta:
        verbose_name = 'Бронь номера для группы работников'
        verbose_name_plural = 'Брони номеров для групп работников'
