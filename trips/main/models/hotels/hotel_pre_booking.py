from datetime import timedelta, date
from decimal import Decimal
from functools import reduce

from django.db import models, transaction

from main.models.agency.agency import Agency
from main.models.hotels.hotel import Hotel
from main.models.hotels.hotel_room_type import HotelRoomType
from main.utils.utils import truncate_str_custom


class HotelPreBookingManager(models.Manager):
    def get_by_natural_key(self, start_date, *hotel_args):
        return self.get(start_date=start_date, hotel=Hotel.objects.get_by_natural_key(*hotel_args))


class HotelPreBooking(models.Model):
    """Предварительная бронь в отеле."""

    class BookingStatusEnum(models.IntegerChoices):
        PRELIMINARY = 0, 'Предварительная'
        CONFIRMED = 1, 'Подтверждённая'
        REALIZED = 2, 'Реализованная'

    agency = models.ForeignKey(Agency, on_delete=models.CASCADE, related_name='hotel_pre_bookings')
    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE, related_name='pre_bookings')
    rooms = models.ManyToManyField(HotelRoomType, through='HotelPreBookingAndRoom', related_name='pre_bookings',
                                   blank=True)
    start_date = models.DateField('Дата заезда')
    end_date = models.DateField('Дата выезда')
    free_cancel_period = models.PositiveSmallIntegerField(
        'Период бесплатной отмены/изменения брони',
        default=10,
    )
    comment = models.TextField('Комментарий', blank=True)
    status = models.PositiveSmallIntegerField(
        'Статус',
        choices=BookingStatusEnum.choices,
        null=True,
    )

    objects = HotelPreBookingManager()

    def natural_key(self):
        # TODO: добавить ещё какое-нибудь поле, чтобы гарантировать уникальность
        return (self.start_date,) + self.hotel.natural_key()

    natural_key.dependencies = ['main.hotel']

    def __str__(self):
        return f"#{self.pk} {self.hotel}, {self.start_date.strftime('%d.%m.%y')} - {self.end_date.strftime('%d.%m.%y')}"

    def short_name(self):
        return f"#{self.pk} · {self.start_date.strftime('%d.%m')} - {self.end_date.strftime('%d.%m')}"

    def long_name(self):
        return f"{self.hotel} · {self.start_date.strftime('%d.%m')} - {self.end_date.strftime('%d.%m')} · " \
               f"{self.get_status_display() or 'Без статуса'}"

    def hotel_and_status_str(self):
        return f"{self.hotel} · {self.get_status_display() or 'Без статуса'}"

    def page_content_title(self):
        return f"Бронь {self.start_date.strftime('%d.%m.%y')} - {self.end_date.strftime('%d.%m.%y')}"

    def duration_nights(self):
        return (self.end_date - self.start_date).days

    def total_rooms_count(self):
        return reduce((lambda a, b: a + b.count), self.hotelprebookingandroom_set.all(), 0)

    def reserved_rooms_count(self):
        return reduce((lambda a, b: a + b.max_reserved_rooms_count()), self.hotelprebookingandroom_set.all(), 0)

    def free_rooms_count(self):
        return self.total_rooms_count() - self.reserved_rooms_count()

    def get_hotel_visit(self):
        return self.trip_hotel_visits.first()

    def get_trip(self):
        hotel_visit = self.get_hotel_visit()
        return hotel_visit.trip if hotel_visit else None

    def free_cancel_date(self):
        return self.start_date - timedelta(days=self.free_cancel_period)

    def days_until_free_cancel(self):
        return max(0, self.days_until_free_cancel_signed())

    def days_until_free_cancel_signed(self):
        return (self.free_cancel_date() - date.today()).days

    def is_inside_free_cancel_danger_period(self):
        return self.days_until_free_cancel() <= self.free_cancel_danger_period()

    def is_inside_free_cancel_warning_period(self):
        return self.free_cancel_danger_period() < self.days_until_free_cancel() <= self.free_cancel_warning_period()

    def available_room_types(self, start_date, end_date):
        rooms = []
        for booking_and_room in self.hotelprebookingandroom_set.all():
            free_count = booking_and_room.free_rooms_count(start_date, end_date)
            if free_count > 0:
                rooms.append(booking_and_room.room_type)
        return rooms

    def is_time_to_cleanup(self):
        return self.start_date >= date.today() and self.is_inside_free_cancel_danger_period() and \
               self.is_empty_or_not_realized()

    def is_empty_or_not_realized(self):
        return not self.has_rooms() or self.needs_to_be_realized()

    def has_rooms(self):
        return self.total_rooms_count() > 0

    def has_free_rooms(self):
        return self.free_rooms_count() > 0

    def needs_to_be_realized(self):
        if not self.has_rooms():
            return False
        return self.status != self.BookingStatusEnum.REALIZED or self.has_free_rooms()

    def is_preliminary(self):
        return self.status == self.BookingStatusEnum.PRELIMINARY

    def is_confirmed(self):
        return self.status == self.BookingStatusEnum.CONFIRMED

    def is_realized(self):
        return self.status == self.BookingStatusEnum.REALIZED

    def cleanup_rooms(self):
        """Убирает из бронирования неиспользованные номера (реализует бронь)."""
        for booking_and_room in self.hotelprebookingandroom_set.all():
            free_count = booking_and_room.free_rooms_count(self.start_date, self.end_date)
            if free_count > 0:
                reduced_count = booking_and_room.count - free_count
                if reduced_count > 0:
                    booking_and_room.count = reduced_count
                    booking_and_room.save()
                else:
                    booking_and_room.delete()
        self.update_status()

    def confirm(self):
        if self.may_confirm():
            self.status = self.BookingStatusEnum.CONFIRMED
            self.save()
            self.update_status()  # Чтобы бронь отметилась как реализованная, если все номера уже заняты

    def may_confirm(self):
        return self.has_rooms() and (self.status == self.BookingStatusEnum.PRELIMINARY or self.status is None)

    def update_status(self):
        if self.may_be_realized():
            self.status = self.BookingStatusEnum.REALIZED
            self.save()

    def may_be_realized(self):
        return self.status == self.BookingStatusEnum.CONFIRMED and self.has_rooms() and not self.has_free_rooms()

    def copy_with_rooms(self, start_date=None, end_date=None):
        with transaction.atomic():
            booking_copy = HotelPreBooking.objects.filter(pk=self.pk).first()
            booking_copy.pk = None  # Способ получить копию модели - просто сбрасываем первичный ключ
            booking_copy.start_date = start_date or self.start_date
            booking_copy.end_date = end_date or self.end_date
            booking_copy.save()
            for booking_and_room in self.hotelprebookingandroom_set.all():
                booking_and_room.pk = None
                booking_and_room.hotel_pre_booking = booking_copy
                booking_and_room.save()
            return booking_copy

    def may_delete(self):
        may_delete = True
        for booking_and_room in self.hotelprebookingandroom_set.all():
            may_delete = not booking_and_room.tourist_room_reservations.exists() and \
                         not booking_and_room.trip_worker_room_reservations.exists()
            if not may_delete:
                break
        return may_delete

    def may_edit_dates(self):
        return not self.get_trip()

    def delete_with_hotel_visits(self):
        if self.may_delete():
            with transaction.atomic():
                for hotel_visit in self.trip_hotel_visits.all():
                    if hotel_visit.pre_bookings.count() <= 1:
                        hotel_visit.delete()  # Если других бронирований нет, то удаляем hotel visit
                    else:
                        hotel_visit.pre_bookings.remove(self)
                        hotel_visit.hotel = hotel_visit.pre_bookings.first().hotel
                        hotel_visit.save()
                self.delete()

    def total_price(self, hotel_visit, nights_count=None):
        return hotel_visit.total_price(booking=self, nights_count=nights_count)

    def remaining_amount_for_guide(self, hotel_visit):
        amount = self.total_price(hotel_visit)
        paid_amount = self.paid_amount_for_guide(hotel_visit)
        return amount - paid_amount

    def paid_amount_for_guide(self, hotel_visit):
        expense_item = self.expense_item_for_guide(hotel_visit)
        return expense_item.amount if expense_item else Decimal(0)

    def total_paid_amount(self, hotel_visit):
        from main.models.money.payment import Payment
        return Payment.get_expenses_sum(self.payment_expense_items.filter(hotel_visit=hotel_visit), is_outgoing=True)

    def expense_item_for_guide(self, hotel_visit):
        from main.models.money.payment import Payment
        expense_items = self.payment_expense_items.filter(hotel_visit=hotel_visit)
        return Payment.get_expense_item_for_guide(expense_items, hotel_visit.trip.agency, is_outgoing=True)

    def add_payment(self, owner, payment_amount, booking_part_amount, payer, account, hotel_visit):
        from main.models.money.payment import Payment
        with transaction.atomic():
            trip = hotel_visit.trip
            payment = Payment.objects.create(
                agency=trip.agency,
                owner=owner,
                payer=payer,
                account=account,
                recipient=None,
                is_outgoing=True,
                amount=payment_amount,
                purpose_text=f"Оплата за гостиницу {truncate_str_custom(self.hotel, 64)}",
                trip=trip,
            )

            from main.models.money.hotel_expense_item import HotelExpenseItem
            HotelExpenseItem.objects.create(
                payment=payment,
                amount=booking_part_amount,
                hotel_visit=hotel_visit,
                booking=self,
            )

            return payment

    @staticmethod
    def free_cancel_danger_period():
        return 5

    @staticmethod
    def free_cancel_warning_period():
        return 10

    @staticmethod
    def annotate_rooms_count(query_set):
        from main.models.hotels.hotel_pre_booking_and_room import HotelPreBookingAndRoom
        from main.utils.queryset_utils import aggregate_subquery
        from django.db.models import functions
        rooms_count_subquery = aggregate_subquery(
            HotelPreBookingAndRoom.objects.filter(hotel_pre_booking=models.OuterRef('pk')),
            aggregate_fun=models.Sum('count'),
            aggregate_by='hotel_pre_booking',
        )
        return query_set.annotate(rooms_count_q=functions.Coalesce(models.Subquery(rooms_count_subquery), 0))

    class Meta:
        verbose_name = 'Предварительное бронирование'
        verbose_name_plural = 'Предварительные бронирования'
