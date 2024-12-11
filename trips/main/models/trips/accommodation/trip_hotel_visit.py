from decimal import Decimal

from django.db import models, transaction
from django.db.models import UniqueConstraint

from main.models.hotels.hotel import Hotel
from main.models.hotels.hotel_pre_booking import HotelPreBooking
from main.models.trips.trip import Trip


class TripHotelVisitManager(models.Manager):
    def get_by_natural_key(self, start_date, *trip_args):
        return self.get(start_date=start_date, trip=Trip.objects.get_by_natural_key(*trip_args))


# TODO: убрать этот класс, вместо этого сделать в TripDay связь многие-ко-многим с бронированиями
class TripHotelVisit(models.Model):
    """Заезд/выезд из гостиницы в конкретную поездку."""
    trip = models.ForeignKey(Trip, on_delete=models.CASCADE, related_name='trip_hotel_visits')
    # TODO: не нужно использовать это поле, правильно использовать hotel из бронирований
    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE, related_name='trip_hotel_visits')
    pre_bookings = models.ManyToManyField(HotelPreBooking, related_name='trip_hotel_visits', blank=True)
    start_date = models.DateField('Дата заезда')
    end_date = models.DateField('Дата выезда')

    objects = TripHotelVisitManager()

    def natural_key(self):
        return (self.start_date,) + self.trip.natural_key()

    natural_key.dependencies = ['main.trip']

    def __str__(self):
        return f"{self.trip}, {self.hotel}, {self.start_date} - {self.end_date}"

    @property
    def duration_nights(self):
        return (self.end_date - self.start_date).days

    def all_roommate_groups(self):
        """"Выдаёт все группы соседей по номерам."""
        groups = []
        groups.extend(self.tourist_roommate_groups.all())
        groups.extend(self.worker_roommate_groups.all())
        return groups

    def all_room_reservations(self):
        """"Возвращает все брони номеров."""
        reservations = []
        for x in self.all_roommate_groups():
            r = x.try_get_room_reservation()
            if r:
                reservations.append(r)
        return reservations

    def all_roommate_groups_in(self, hotel):
        groups = []
        for x in self.all_roommate_groups():
            r = x.try_get_room_reservation()
            if r and r.hotel_pre_booking_and_room.hotel_pre_booking.hotel == hotel:
                groups.append(x)
        return groups

    def has_room_reservations(self):
        return self.tourist_groups_with_room().exists() or self.worker_groups_with_room().exists()

    def tourist_groups_with_room(self):
        return self.tourist_roommate_groups.exclude(room_reservation__isnull=True)

    def tourist_groups_who_should_have_room(self):
        return self.tourist_roommate_groups.filter(is_room_needed=True)

    def tourist_groups_left_to_accommodate(self):
        return self.tourist_groups_who_should_have_room().filter(room_reservation__isnull=True)

    def worker_groups_with_room(self):
        return self.worker_roommate_groups.exclude(room_reservation__isnull=True)

    def worker_groups_who_should_have_room(self):
        return self.worker_roommate_groups.filter(is_room_needed=True)

    def worker_groups_left_to_accommodate(self):
        return self.worker_groups_who_should_have_room().filter(room_reservation__isnull=True)

    def tourists_left_to_accommodate_count(self):
        return self.get_roommates_count(self.tourist_groups_left_to_accommodate())

    def workers_left_to_accommodate_count(self):
        return self.get_roommates_count(self.worker_groups_left_to_accommodate())

    def tourists_with_room_count(self):
        return self.get_roommates_count(self.tourist_groups_with_room())

    def workers_with_room_count(self):
        return self.get_roommates_count(self.worker_groups_with_room())

    def tourists_who_should_have_room_count(self):
        return self.get_roommates_count(self.tourist_groups_who_should_have_room())

    def workers_who_should_have_room_count(self):
        return self.get_roommates_count(self.worker_groups_who_should_have_room())

    def all_have_rooms(self):
        return not self.tourist_groups_left_to_accommodate().exists() and not self.worker_groups_left_to_accommodate().exists()

    def get_next_room_number(self, room_type):
        return 1 + max(
            [x.room_number for x in self.all_room_reservations()
             if x.hotel_pre_booking_and_room.room_type == room_type],
            default=0
        )

    def total_price(self, booking=None, nights_count=None):
        # TODO: переписать с использованием trip_money_utils
        nights_count = nights_count or self.duration_nights
        prices = []
        for roommates_group in self.all_roommate_groups():
            reservation = roommates_group.try_get_room_reservation()
            if reservation:
                if not booking or reservation.hotel_pre_booking_and_room.hotel_pre_booking == booking:
                    room_type = reservation.hotel_pre_booking_and_room.room_type
                    price = room_type.price
                    if room_type.price_single and roommates_group.roommates_count() == 1:
                        price = room_type.price_single
                    if price:
                        prices.append(price * nights_count)
        return sum(prices, Decimal(0))

    def get_day_number(self):
        return self.trip.get_day_number(self.start_date)

    def get_visit_day_number(self, date):
        return (date - self.start_date).days + 1

    def get_active_sidebar_item(self):
        return f"accommodation_day_{self.get_day_number()}"

    def all_bookings_realized(self):
        return self.pre_bookings.exists() and all(x.is_realized() for x in self.pre_bookings.all())

    def may_delete(self):
        return all(x.may_delete() for x in self.pre_bookings.all())

    def delete_with_bookings(self):
        if self.may_delete():
            with transaction.atomic():
                self.pre_bookings.all().delete()
                self.delete()

    @staticmethod
    def get_roommates_count(roommate_groups_qs):
        # TODO: переписать этот метод и все, где он вызывается, с использованием trip_money_utils
        return roommate_groups_qs.annotate(roommates_count=models.Count('roommates')). \
            aggregate(count=models.Sum('roommates_count'))['count'] or 0

    class Meta:
        verbose_name = 'Заезд/выезд из гостиницы'
        verbose_name_plural = 'Заезды/выезды из гостиниц'
        constraints = [
            UniqueConstraint(fields=['trip', 'hotel', 'start_date'], name='%(app_label)s_%(class)s_is_unique'),
        ]
