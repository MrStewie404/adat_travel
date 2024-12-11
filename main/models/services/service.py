import datetime
from collections import OrderedDict
from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import UniqueConstraint, Q

from main.models.agency.agency import Agency
from main.models.directory.city import City
from main.models.services.supplier import Supplier
from main.models.services.service_label import ServiceLabel
from main.templatetags.pluralize_ru import pluralize_ru
from main.utils.season_date import SeasonDate


class ServiceManager(models.Manager):
    def get_by_natural_key(self, name, agency__name, supplier__name, supplier__agency, *city_args):
        return self.get(
            name=name,
            agency=Agency.objects.get_by_natural_key(agency__name) if agency__name else None,
            supplier=Supplier.objects.get_by_natural_key(supplier__name, supplier__agency) if supplier__name else None,
            city=City.objects.get_by_natural_key(*city_args) if city_args[0] else None,
        )


class Service(models.Model):
    """Туристическая услуга."""
    agency = models.ForeignKey(Agency, on_delete=models.CASCADE, related_name='services', blank=True, null=True)
    labels = models.ManyToManyField(ServiceLabel, related_name='services', blank=True)
    name = models.CharField('Название', max_length=256)
    city = models.ForeignKey(City, on_delete=models.SET_NULL, related_name='services', blank=True, null=True)
    address = models.CharField('Адрес', max_length=256, blank=True)
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE, related_name='services', blank=True, null=True)
    min_group_size = models.PositiveSmallIntegerField('Минимальный размер группы', default=1)
    max_group_size = models.PositiveSmallIntegerField('Максимальный размер группы', blank=True, null=True)
    duration_minutes = models.PositiveSmallIntegerField('Длительность, мин')
    description = models.TextField('Описание', blank=True)
    is_archived = models.BooleanField('Архив', default=False)  # Архивную услугу нельзя выбрать в турах

    empty_supplier_label = "Не задан"
    empty_city_label = "Не задан"

    objects = ServiceManager()

    def natural_key(self):
        agency_key = self.agency.natural_key() if self.agency else (None,)
        city_key = self.city.natural_key() if self.city else (None, None,)
        supplier_key = self.supplier.natural_key() if self.supplier else (None, None,)
        return (self.name,) + agency_key + supplier_key + city_key

    natural_key.dependencies = ['main.agency', 'main.city', 'main.supplier']

    @property
    def duration_hours(self):
        if self.duration_minutes is None:
            return None
        return self.duration_minutes // 60

    @duration_hours.setter
    def duration_hours(self, value):
        self.duration_minutes = value * 60

    def duration_extra_minutes(self):
        return (self.duration_minutes or 0) % 60

    def __str__(self):
        s = ''
        if self.city:
            s = s + f"{self.city} · "
        s = s + self.name
        if self.supplier:
            s = s + f" · {self.supplier}"
        return s

    def is_available_for(self, date=None, person_count=None, allow_smaller_person_count=False,
                         allow_larger_person_count=False):
        if date is None and person_count is None:
            raise ValueError("Должен быть задан хотя бы один аргумент: 'date' или 'person_count'.")
        if person_count:
            if not allow_larger_person_count and self.max_group_size and person_count > self.max_group_size:
                return False
            if not allow_smaller_person_count and person_count < self.min_group_size:
                return False
        if date and not self.get_price_model(date):
            return False
        return True

    def get_price(self, date, person_count, allow_smaller_person_count=False, allow_larger_person_count=False):
        is_available = date and person_count and \
                       self.is_available_for(
                           date=date,
                           person_count=person_count,
                           allow_smaller_person_count=allow_smaller_person_count,
                           allow_larger_person_count=allow_larger_person_count,
                       )
        if not is_available:
            raise ValueError("Услуга недоступна на заданную дату или для заданного количества человек.")
        return self.get_price_model(date).get_price(person_count=max(person_count, self.min_group_size))

    def get_price_today(self, person_count, allow_smaller_person_count=False):
        return self.get_price(date=datetime.date.today(), person_count=person_count,
                              allow_smaller_person_count=allow_smaller_person_count)

    def get_price_model(self, date):
        date = SeasonDate.from_date(date)
        return self.prices.filter(
            start_date__lte=date,
            end_date__gte=date,
        ).first()

    def get_most_expensive_price_model(self):
        return self.prices.order_by('-cost').first()

    def trips_with_contracts(self):
        contracts_by_trip = OrderedDict()
        for trip in self.trips.all():
            contracts_by_trip[trip] = []
        for contract in self.client_contracts.all():
            contracts_by_trip.setdefault(contract.trip, []).append(contract)
        return contracts_by_trip.items()

    def group_size_str(self):
        if self.max_group_size:
            return f"от {self.min_group_size} до {self.max_group_size}"
        return f"от {self.min_group_size}"

    def prices_str(self):
        price_str_list = [x.short_price_str() for x in self.prices.all()]
        return '\n'.join(price_str_list)

    def add_price(self, cost, price_type, start_date=None, end_date=None):
        kwargs = dict(
            service=self,
            cost=cost,
            price_type=price_type,
        )
        if start_date:
            kwargs.update(start_date=start_date)
        if end_date:
            kwargs.update(end_date=end_date)
        from main.models.services.service_price import ServicePrice
        return ServicePrice.objects.create(**kwargs)

    def add_person_price(self, cost, start_date=None, end_date=None):
        from main.models.services.service_price import ServicePrice
        return self.add_price(cost, ServicePrice.PriceTypeEnum.PER_PERSON, start_date, end_date)

    def add_group_price(self, cost, start_date=None, end_date=None):
        from main.models.services.service_price import ServicePrice
        return self.add_price(cost, ServicePrice.PriceTypeEnum.PER_GROUP, start_date, end_date)

    def validate_unique(self, exclude=None):
        super().validate_unique(exclude=exclude)
        agency = self.agency
        agency_filter = (Q(agency=None) | Q(agency=agency)) if agency else Q()
        if Service.objects.exclude(pk=self.pk).filter(agency_filter, name=self.name, city=self.city,
                                                      supplier=self.supplier).exists():
            raise ValidationError("Услуга с таким названием уже существует в том же городе и у того же контрагента.",
                                  code='name_not_unique')

    def may_delete(self):
        return not self.client_contracts.exists()

    class Meta:
        verbose_name = 'Услуга'
        verbose_name_plural = 'Услуги'
        permissions = [
            ('manage_services', 'Пользователь может управлять услугами, но не удалять их (#наше)'),
            ('delete_services', 'Пользователь может удалять услуги (#наше)'),
        ]
