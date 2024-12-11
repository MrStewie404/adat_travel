import abc

from django.db import models
from django.db.models import UniqueConstraint

from main.models.abc_model import ABCModel
from main.models.trips.accommodation.trip_hotel_visit import TripHotelVisit


class AbstractTripRoommatesGroupManager(models.Manager, metaclass=abc.ABCMeta):
    def get_by_natural_key(self, visit__start_date, visit__trip__name, visit__trip__start_date, visit__trip__agency,
                           *person_args):
        hotel_visit = TripHotelVisit.objects.get_by_natural_key(visit__start_date, visit__trip__name,
                                                                visit__trip__start_date, visit__trip__agency)
        roommates_selector = []
        # Персону нам могут не передать, см. комментарий в методе natural_key.
        if len(person_args) > 0:
            roommates_selector.append(self.person_class().objects.get_by_natural_key(*person_args))
        return self.get(trip_hotel_visit=hotel_visit, roommates__in=roommates_selector)

    @staticmethod
    @abc.abstractmethod
    def person_class():
        pass


class AbstractTripRoommatesGroup(ABCModel):
    """Абстрактная модель: группа соседей по номеру (т.е. живущих в одном номере в конкретной гостинице)."""

    @staticmethod
    def create_trip_hotel_visit(related_name):
        return models.ForeignKey(TripHotelVisit, on_delete=models.CASCADE, related_name=related_name)

    @property
    @abc.abstractmethod
    def trip_hotel_visit(self):
        """Абстрактное поле."""
        pass

    @staticmethod
    def create_roommates(person_class, related_name):
        return models.ManyToManyField(person_class, related_name=related_name, blank=True)

    @property
    @abc.abstractmethod
    def roommates(self):
        """Абстрактное поле."""
        pass

    name = models.CharField('Уникальное имя (в рамках одного заезда)', max_length=32)  # Для fixtures-ов
    is_room_needed = models.BooleanField('Нужен номер', default=True)

    def natural_key(self):
        natural_key = self.trip_hotel_visit.natural_key()
        # Django при десериализации вызывает natural_key() у модели, в которой ещё нет ни pk, ни полей many-to-many.
        if self.pk and self.roommates.exists():
            natural_key = natural_key + self.roommates.first().natural_key()
        return natural_key

    # natural_key.dependencies = ['main.triphotelvisit', 'main.person'] # Зависимости определены в производных классах

    def __str__(self):
        return f"Roommates ({self.trip_hotel_visit})"

    @property
    def persons(self):
        return list(self.roommates.all())

    def roommates_to_string(self, property_getter, delimiter):
        return delimiter.join(property_getter(x) for x in self.roommates.all())

    def try_get_room_reservation(self):
        return getattr(self, 'room_reservation', None)

    def new_room_reservation(self):
        from main.models.trips.accommodation.trip_room_reservation import TripRoomReservation
        from main.models.trips.accommodation.trip_worker_room_reservation import TripWorkerRoomReservation
        return TripRoomReservation(roommates_group=self) if self.is_tourists_group() \
            else TripWorkerRoomReservation(roommates_group=self)

    def get_desired_room_type(self):
        from main.models.trips.tourists.trip_company import TripCompany
        return TripCompany.AccommodationTypeEnum.NONE

    def roommates_count(self):
        return self.roommates.count()

    @abc.abstractmethod
    def is_tourists_group(self):
        pass

    @property
    def trip(self):
        return self.trip_hotel_visit.trip

    def may_change_reservation(self):
        reservation = self.try_get_room_reservation()
        return not reservation or not reservation.hotel_pre_booking_and_room.hotel_pre_booking.is_realized()

    def may_change_roommates(self):
        return not self.try_get_room_reservation()

    @staticmethod
    def remove_from_roommates_group(person, group):
        group.roommates.remove(person)
        reservation = group.try_get_room_reservation()
        if reservation:
            reservation.delete()
        if not group.roommates.exists():
            group.delete()

    class Meta:
        abstract = True
        constraints = [
            UniqueConstraint(fields=['trip_hotel_visit', 'name'], name='%(app_label)s_%(class)s_is_unique'),
        ]
