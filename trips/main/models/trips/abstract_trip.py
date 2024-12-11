import abc
from datetime import timedelta, datetime, date, time
from decimal import Decimal

from django.db import models

from main.models.abc_model import ABCModel
from main.models.agency.agency import Agency
from main.models.directory.city import City
from main.models.services.service import Service
from main.templatetags.pluralize_ru import pluralize_ru


class AbstractTrip(ABCModel):
    """Абстрактная модель: тур или маршрут (т.е. шаблон тура)."""

    @staticmethod
    def create_agency(related_name):
        return models.ForeignKey(Agency, on_delete=models.CASCADE, related_name=related_name)

    @property
    @abc.abstractmethod
    def agency(self):
        """Абстрактное поле."""
        pass

    @staticmethod
    def create_cities(through, related_name):
        return models.ManyToManyField(City, through=through, related_name=related_name, blank=True)

    @property
    @abc.abstractmethod
    def cities(self):
        """Абстрактное поле."""
        pass

    @staticmethod
    def create_services(through, related_name):
        return models.ManyToManyField(Service, through=through, related_name=related_name, blank=True)

    @property
    @abc.abstractmethod
    def services(self):
        """Абстрактное поле."""
        pass

    # TODO: разобраться, почему в классе Route перестаёт работать поле duration_nights, если раскомментировать его тут
    # @property
    # @abc.abstractmethod
    # def duration_nights(self):
    #     """Абстрактное поле."""
    #     pass

    @staticmethod
    def create_duration_nights():
        return models.PositiveSmallIntegerField('Длительность (ночей)')

    name = models.CharField('Название', max_length=256)
    description = models.TextField('Описание', blank=True)
    is_food_preferences_used = models.BooleanField('Учёт предпочтений по питанию', default=True)
    # Архивный маршрут нельзя выбрать для новых туров, а архивный тур не отображается в списке активных
    is_archived = models.BooleanField('Архив', default=False)
    start_time = models.TimeField('Время начала', blank=True, null=True)
    end_time = models.TimeField('Время окончания', blank=True, null=True)
    transport = models.CharField('Транспорт', max_length=64, blank=True)

    def __str__(self):
        return self.name

    @property
    def duration_days(self):
        """Длительность тура в днях, считая день отъезда."""
        return self.duration_nights + 1

    def days_nights_str(self):
        return f"{self.duration_days}/{self.duration_nights}"

    def duration_str(self):
        days = self.duration_days
        if days > 1:
            return f"{days} {pluralize_ru(days, 'день,дня,дней')}"

        end_date_time = datetime.combine(date.min, self.end_time or time(00, 00))
        start_date_time = datetime.combine(date.min, self.start_time or time(00, 00))
        time_delta = end_date_time - start_date_time
        hours = int(time_delta.total_seconds() // 3600)
        return f"{hours} час{pluralize_ru(hours, ',а,ов')}"

    def trip_day_numbers(self):
        return list(range(1, self.duration_days + 1))

    @property
    def is_excursion(self):
        return self.duration_nights <= 0

    @abc.abstractmethod
    def get_city(self, day_number, objective):
        pass

    @abc.abstractmethod
    def get_tripandservice_set(self, day_number):
        """Должен возвращать отсортированный список моделей TripAndService."""
        pass

    def get_services(self, day_number):
        """Возвращает отсортированный список услуг."""
        return [x.service for x in self.get_tripandservice_set(day_number)]

    def get_services_by_day(self):
        services_by_day = []
        for day_number in self.trip_day_numbers():
            services_by_day.append((day_number, self.get_services_info(day_number)))
        return services_by_day

    def get_services_info(self, day_number):
        trip_and_service_set = self.get_tripandservice_set(day_number)
        from main.models.trips.schedule.abstract_trip_and_city import AbstractTripAndCity
        overnight_city = self.get_city(day_number, objective=AbstractTripAndCity.ObjectiveEnum.OVERNIGHT)
        sightseeing_city = self.get_city(day_number, objective=AbstractTripAndCity.ObjectiveEnum.SIGHTSEEING)
        day_model = self.days.filter(day=day_number).first()
        prices_by_type = self.get_service_prices_evaluation(day_number)
        from main.models.services.abstract_price import AbstractPrice
        price_per_person = prices_by_type[AbstractPrice.PriceTypeEnum.PER_PERSON]
        price_per_group = prices_by_type[AbstractPrice.PriceTypeEnum.PER_GROUP]
        return {
            'caption': day_model.caption if day_model else '',
            'overnight_city': overnight_city,
            'sightseeing_city': sightseeing_city,
            'tripandservice_set': trip_and_service_set,
            'day_price_per_person': price_per_person['value'],
            'day_price_per_group': price_per_group['value'],
            'day_price_services_count': price_per_person['count'] + price_per_group['count'],
        }

    def get_service_prices_evaluation(self, day):
        """
        Вычисляет оценочную суммарную стоимость услуг за указанный день;
        отдельно считает стоимость на одного человека + на группу.
        """
        from main.models.services.abstract_price import AbstractPrice
        prices_by_type = {
            AbstractPrice.PriceTypeEnum.PER_PERSON: {'value': Decimal(0), 'count': 0},
            AbstractPrice.PriceTypeEnum.PER_GROUP: {'value': Decimal(0), 'count': 0},
        }
        for trip_and_service in self.get_tripandservice_set(day):
            if hasattr(trip_and_service, 'date'):
                price_model = trip_and_service.service.get_price_model(trip_and_service.date)
            else:
                price_model = trip_and_service.service.get_most_expensive_price_model()
            if price_model:
                prices_by_type[price_model.price_type]['value'] += price_model.get_price(person_count=1)
                prices_by_type[price_model.price_type]['count'] += 1
        return prices_by_type

    def full_schedule_str(self):
        lines = []
        for day_number in self.trip_day_numbers():
            day_model = self.days.filter(day=day_number).first()
            lines.append(f"День {day_number}. {day_model.caption if day_model else '(Без названия)'}.")
            from main.models.trips.schedule.trip_and_city import TripAndCity
            city_sight = self.get_city(day_number, objective=TripAndCity.ObjectiveEnum.SIGHTSEEING)
            city_night = self.get_city(day_number, objective=TripAndCity.ObjectiveEnum.OVERNIGHT)
            lines.append(f"Город посещения: {city_sight or 'не выбран'}")
            lines.append(f"Город ночёвки: {city_night or 'не выбран'}")
            services_str = ' · '.join(x.name for x in self.get_services(day_number))
            lines.append(services_str)
            lines.append("")
        return '\n'.join(lines)

    class Meta:
        abstract = True
