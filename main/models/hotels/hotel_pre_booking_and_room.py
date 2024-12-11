from datetime import timedelta

from django.db import models
from django.db.models import UniqueConstraint

from main.models.hotels.hotel_pre_booking import HotelPreBooking
from main.models.hotels.hotel_room_type import HotelRoomType


class HotelPreBookingAndRoomManager(models.Manager):
    def get_by_natural_key(self, booking__start_date, hotel__name, hotel__city__name, hotel__agency__name,
                           room_type__name):
        hotel_args = (hotel__name, hotel__agency__name, hotel__city__name, hotel__agency__name)
        return self.get(
            hotel_pre_booking=HotelPreBooking.objects.get_by_natural_key(booking__start_date, *hotel_args),
            room_type=HotelRoomType.objects.get_by_natural_key(room_type__name, *hotel_args),
        )


class HotelPreBookingAndRoom(models.Model):
    """Связь "предварительные бронирования - комнаты"."""
    hotel_pre_booking = models.ForeignKey(HotelPreBooking, on_delete=models.CASCADE)
    room_type = models.ForeignKey(HotelRoomType, on_delete=models.CASCADE)
    count = models.PositiveSmallIntegerField('Количество', default=0)

    objects = HotelPreBookingAndRoomManager()

    def natural_key(self):
        booking = self.hotel_pre_booking
        hotel = booking.hotel
        agency_name = hotel.agency.name if hotel.agency else None
        return (booking.start_date, hotel.name, hotel.city.name, agency_name, self.room_type.name)

    natural_key.dependencies = ['main.hotelprebooking', 'main.hotelroomtype']

    def __str__(self):
        return f"{self.hotel_pre_booking}, {self.room_type}"

    def all_room_reservations(self):
        reservations = []
        reservations.extend(self.tourist_room_reservations.all())
        reservations.extend(self.trip_worker_room_reservations.all())
        return reservations

    def max_reserved_rooms_count(self, start_date=None, end_date=None):
        reservations_by_date = dict()
        for reservation in self.all_room_reservations():
            hotel_visit = reservation.roommates_group.trip_hotel_visit
            start_date_cur = hotel_visit.start_date
            if start_date:
                start_date_cur = max(start_date_cur, start_date, self.hotel_pre_booking.start_date)
            end_date_cur = hotel_visit.end_date
            if end_date:
                end_date_cur = min(end_date_cur, end_date, self.hotel_pre_booking.end_date)
            if start_date_cur < end_date_cur:
                for day in range((end_date_cur - start_date_cur).days):
                    date = start_date_cur + timedelta(days=day)
                    reservations_by_date[date] = reservations_by_date.setdefault(date, 0) + 1
        return max(reservations_by_date.values(), default=0)

    def free_rooms_count(self, start_date=None, end_date=None):
        reserv_count = self.max_reserved_rooms_count(start_date, end_date)
        return max(0, self.count - reserv_count)

    def may_reserve_next_room(self, hotel_visit):
        return not self.hotel_pre_booking.is_realized() and \
               self.free_rooms_count(hotel_visit.start_date, hotel_visit.end_date) > 0

    def get_room_and_count_str(self, hotel_visit):
        rooms_cnt = self.free_rooms_count(hotel_visit.start_date, hotel_visit.end_date)
        room_type = self.room_type.name
        hotel_prefix = ""
        if hotel_visit.pre_bookings.count() > 1:
            hotel_prefix = f"{self.room_type.hotel.name} · "
        return f"{hotel_prefix}{room_type} (свободно: {rooms_cnt})"

    class Meta:
        verbose_name = 'Предварительное бронирование - комната'
        verbose_name_plural = 'Предварительные бронирования - комнаты'
        constraints = [
            UniqueConstraint(fields=['hotel_pre_booking', 'room_type'], name='%(app_label)s_%(class)s_is_unique'),
        ]
