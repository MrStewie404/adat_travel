from decimal import Decimal

from django.db import models, transaction
from django.db.models import UniqueConstraint

from main.models.services.service import Service
from main.models.trips.schedule.abstract_trip_and_service import AbstractTripAndService
from main.models.trips.trip import Trip
from main.utils.utils import truncate_str_custom


class TripAndServiceManager(models.Manager):
    def get_by_natural_key(self, day, trip__name, trip__start_date, trip__agency, *service_args):
        return self.get(
            day=day,
            trip=Trip.objects.get_by_natural_key(trip__name, trip__start_date, trip__agency),
            service=Service.objects.get_by_natural_key(*service_args),
        )


class TripAndService(AbstractTripAndService):
    """Связь "туры - услуги"."""
    trip = models.ForeignKey(Trip, on_delete=models.CASCADE)

    objects = TripAndServiceManager()

    def natural_key(self):
        return (self.day,) + self.trip.natural_key() + self.service.natural_key()

    natural_key.dependencies = ['main.trip', 'main.service']

    def __str__(self):
        return f"{self.trip}, {self.date}, {self.service}"

    @property
    def date(self):
        if not self.day:
            return None
        return self.trip.get_date(self.day)

    def get_price(self, default):
        tourists_count = self.trip.busy_seats_count()
        if tourists_count > 0 and self.service.is_available_for(date=self.date, person_count=tourists_count):
            return self.service.get_price(date=self.date, person_count=tourists_count)
        return default

    def get_price_or_zero(self):
        return self.get_price(default=Decimal(0))

    def remaining_amount_for_guide(self):
        amount = self.get_price_or_zero()
        paid_amount = self.paid_amount_for_guide()
        return amount - paid_amount

    def paid_amount_for_guide(self):
        expense_item = self.expense_item_for_guide()
        return expense_item.amount if expense_item else Decimal(0)

    def total_paid_amount(self):
        from main.models.money.payment import Payment
        return Payment.get_expenses_sum(self.payment_expense_items.all(), is_outgoing=True)

    def expense_item_for_guide(self):
        from main.models.money.payment import Payment
        return Payment.get_expense_item_for_guide(self.payment_expense_items, self.trip.agency, is_outgoing=True)

    def add_payment(self, owner, payment_amount, service_part_amount, payer, account):
        from main.models.money.payment import Payment
        with transaction.atomic():
            payment = Payment.objects.create(
                agency=self.trip.agency,
                owner=owner,
                payer=payer,
                account=account,
                recipient=self.service.supplier.as_payment_party(save=True) if self.service.supplier else None,
                is_outgoing=True,
                amount=payment_amount,
                purpose_text=f"Оплата за услугу {truncate_str_custom(self.service.name, 64)}",
                trip=self.trip,
            )

            from main.models.money.trip_service_expense_item import TripServiceExpenseItem
            TripServiceExpenseItem.objects.create(
                payment=payment,
                amount=service_part_amount,
                trip_and_service=self,
            )

            return payment

    class Meta(AbstractTripAndService.Meta):
        verbose_name = 'Тур - услуга'
        verbose_name_plural = 'Туры - услуги'
        constraints = [
            UniqueConstraint(fields=['trip', 'service', 'day'], name='%(app_label)s_%(class)s_is_unique'),
        ]
