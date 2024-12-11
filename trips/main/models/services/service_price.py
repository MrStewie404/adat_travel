import datetime

from django.core.exceptions import ValidationError
from django.db import models

from main.models.services.abstract_price import AbstractPrice
from main.models.services.service import Service
from main.templatetags import format_extensions
from main.utils.season_date import SeasonDate


class ServicePriceManager(models.Manager):
    def get_by_natural_key(self, *service_args):
        return self.get(service=Service.objects.get_by_natural_key(*service_args))


class ServicePrice(AbstractPrice):
    """Стоимость услуги."""
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name='prices')
    start_date = models.DateField('Дата начала', default=datetime.date(datetime.MINYEAR, 1, 1))
    end_date = models.DateField('Дата окончания', default=datetime.date(datetime.MINYEAR, 12, 31))

    objects = ServicePriceManager()

    def natural_key(self):
        # TODO: добавить дату начала, когда на сайте будут поддержаны сезонные цены
        return self.service.natural_key()

    natural_key.dependencies = ['main.service']

    def __str__(self):
        return f"{self.service}, {self.cost} ({self.start_date} - {self.end_date})"

    def short_price_str(self):
        cost_str = format_extensions.currency(self.cost, precision=0)
        if self.start_date == SeasonDate(1, 1) and self.end_date == SeasonDate(12, 31):
            return cost_str
        return f"{cost_str} ({self.start_date.strftime('%d.%m')} - {self.end_date.strftime('%d.%m')})"

    def clean_dates(self):
        """Год заменяем на фиксированный, т.к. он не используется и так легче сравнивать даты."""
        self.start_date = SeasonDate.from_date(self.start_date)
        self.end_date = SeasonDate.from_date(self.end_date)

    def clean(self):
        super().clean()
        self.clean_dates()
        if self.start_date > self.end_date:
            raise ValidationError("Дата начала не должна быть позже даты окончания", code='service_price_bad_dates')

    def validate_unique(self, exclude=None):
        super().validate_unique(exclude=exclude)
        duplicate_prices = ServicePrice.objects.exclude(pk=self.pk).filter(
            service=self.service,
            start_date__lte=self.end_date,
            end_date__gte=self.start_date,
        )
        if duplicate_prices.exists():
            raise ValidationError("Диапазон дат не должен пересекаться с другими сезонами",
                                  code='service_price_bad_dates')

    def save(self, *args, **kwargs):
        # Если мы создаём модель в коде, то при сохранении стоит для надёжности вызвать full_clean.
        self.full_clean()
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = 'Стоимость услуги'
        verbose_name_plural = 'Стоимость услуг'
