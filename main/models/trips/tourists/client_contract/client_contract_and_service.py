from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import UniqueConstraint

from main.models.services.abstract_price import AbstractPrice
from main.models.services.service import Service
from main.models.trips.tourists.client_contract.client_contract import ClientContract
from main.models.trips.schedule.trip_and_service import TripAndService
from main.models.utils import create_price_field


class ClientContractAndService(AbstractPrice):
    """Связь "договоры - услуги"."""
    contract = models.ForeignKey(ClientContract, on_delete=models.CASCADE)
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    # Дополнительно сохраняем опциональную ссылку на таблицу "туры-услуги", где хранится день тура.
    trip_and_service = models.ForeignKey(TripAndService, on_delete=models.SET_NULL, blank=True, null=True)
    trip_day = models.PositiveSmallIntegerField('День тура', validators=[MinValueValidator(1)])
    tourist_count = models.PositiveSmallIntegerField('Количество гостей, заказавших услугу',
                                                     validators=[MinValueValidator(1)])
    # Сохраняем стоимость на момент подписания договора, т.к. в услуге стоимость может меняться
    cost = create_price_field('Фактическая стоимость')
    order_id = models.SmallIntegerField(default=-1)

    def __str__(self):
        return f"{self.contract} · {self.service}"

    def save(self, *args, **kwargs):
        if not self.pk and self.order_id < 0:
            max_id = ClientContractAndService.objects.filter(contract=self.contract, trip_day=self.trip_day).\
                aggregate(max_id=models.Max('order_id'))['max_id']
            self.order_id = max(max_id + 1, 0) if max_id is not None else 0
        super().save(*args, **kwargs)

    @property
    def date(self):
        return self.contract.trip.get_date(self.trip_day)

    def total_price(self):
        return self.get_price(self.tourist_count)

    class Meta:
        verbose_name = 'Договор - услуга'
        verbose_name_plural = 'Договоры - услуги'
        ordering = ('order_id',)
        constraints = [
            UniqueConstraint(fields=['contract', 'trip_and_service'], name='%(app_label)s_%(class)s_is_unique'),
        ]
