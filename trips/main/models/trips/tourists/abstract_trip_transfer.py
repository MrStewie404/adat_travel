from django.db import models
from django.db.models import UniqueConstraint
from django.utils import timezone

from main.models.trips.tourists.trip_and_client import TripAndClient


class AbstractTripTransfer(models.Model):
    """Абстрактная модель: информация о трансфере."""

    class TransferTypeEnum(models.TextChoices):
        ARRIVAL = 'ARRIVAL', 'Заезд'
        DEPARTURE = 'DEPARTURE', 'Отъезд'

        __empty__ = '(Выберите тип трансфера)'

    trip_and_client = models.ForeignKey(TripAndClient, on_delete=models.CASCADE, related_name='transfers')
    transfer_type = models.CharField(
        'Тип трансфера',
        max_length=16,
        choices=TransferTypeEnum.choices,
        blank=False,
    )
    date_time = models.DateTimeField('Дата/время')
    need_transfer = models.BooleanField('Нужен трансфер', default=False)
    comment = models.TextField('Комментарий', blank=True)

    def __str__(self):
        return f"{self.trip_and_client}, {self.transfer_type}, " \
               f"{self.date_time_local.strftime('%d.%m.%y %H:%M')}"

    @property
    def date_time_local(self):
        """Этот метод стоит использовать только непосредственно для печати в строку (strftime)
        или для получения правильной даты (см. CustomTimezoneMiddleware - там мы задаём текущим московское время).
        Любые другие операуии с датой/временем рекомендуется выполнять в часовом поясе UTC."""
        return timezone.localtime(self.date_time)

    def transfer_and_client_comment(self):
        comment = self.trip_and_client.client.full_comment()
        if self.comment:
            transfer_comment = f"Трансфер: {self.comment}"
            return f"{comment}\n{transfer_comment}" if comment else transfer_comment
        return comment

    def short_date_time_str(self):
        return self.date_time_local.strftime('%d.%m(%H:%M)')

    class Meta:
        abstract = True
        constraints = [
            UniqueConstraint(fields=['trip_and_client', 'transfer_type'], name='%(app_label)s_%(class)s_is_unique'),
        ]
