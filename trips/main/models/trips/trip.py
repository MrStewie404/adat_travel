import itertools
from collections import OrderedDict
from datetime import timedelta, date, time, datetime

from django.db import models, transaction
from django.db.models import UniqueConstraint
from django.forms import model_to_dict

from main.models.agency.agency import Agency
from main.models.clients.client import Client
from main.models.directory.restaurant import Restaurant
from main.models.hotels.hotel import Hotel
from main.models.routes.route import Route
from main.models.trips.abstract_trip import AbstractTrip
from main.models.trips.departure_point import DeparturePoint
from main.models.utils import create_price_field
from main.models.workers.trip_worker import TripWorker
from main.utils.utils import django_date_str


class TripManager(models.Manager):
    def get_by_natural_key(self, name, start_date, agency__name):
        return self.get(name=name, start_date=start_date, agency=Agency.objects.get_by_natural_key(agency__name))


class Trip(AbstractTrip):
    """Поездка по маршруту, путешествие."""

    class TripStateEnum(models.TextChoices):
        FORMING = 'FORMING', 'Формируется'
        FORMED = 'FORMED', 'Сформирован'
        ON_AGREEMENT = 'ON_AGREEMENT', 'По согласованию'
        CLOSED = 'CLOSED', 'Закрыт'

        __empty__ = '(Статус)'

    class TripCategoryEnum(models.TextChoices):
        REGULAR = 'REGULAR', 'Регулярный'
        INDIVIDUAL = 'INDIVIDUAL', 'Индивидуальный'
        CORPORATE = 'CORPORATE', 'Корпоративный'

        __empty__ = '(Категория)'

    class TripSortEnum(models.TextChoices):
        BY_DATE = 'BY_DATE', 'По дате'
        BY_NAME = 'BY_NAME', 'По названию'
        BY_STATE = 'BY_STATE', 'По статусу'

    agency = AbstractTrip.create_agency(related_name='trips')
    cities = AbstractTrip.create_cities(through='TripAndCity', related_name='trips')
    # Необязательную ссылку на маршрут оставляем только для справки
    route = models.ForeignKey(Route, on_delete=models.SET_NULL, blank=True, null=True, related_name='trips')
    tourists = models.ManyToManyField(Client, through='TripAndClient', related_name='trips', blank=True)
    workers = models.ManyToManyField(TripWorker, through='TripAndTripWorker', related_name='trips', blank=True)
    hotels = models.ManyToManyField(Hotel, through='TripHotelVisit', related_name='trips', blank=True)
    restaurants = models.ManyToManyField(Restaurant, through='TripRestaurantVisit', related_name='trips', blank=True)
    services = AbstractTrip.create_services(through='TripAndService', related_name='trips')
    departure_points = models.ManyToManyField(DeparturePoint, related_name='trips', blank=True)
    route_name = models.CharField('Название маршрута', max_length=256)
    start_date = models.DateField('Дата начала')
    end_date = models.DateField('Дата окончания')
    max_tourists_count = models.PositiveSmallIntegerField('Максимальное количество гостей')
    state = models.CharField(
        'Статус',
        max_length=32,
        choices=TripStateEnum.choices,
        blank=True,
    )
    category = models.CharField(
        'Категория',
        max_length=16,
        choices=TripCategoryEnum.choices,
        default=TripCategoryEnum.REGULAR,
    )
    price = create_price_field('Стоимость')
    default_prepayment = create_price_field('Аванс', default=0)
    group_chat_link = models.URLField('Ссылка на группу в WhatsApp', blank=True)
    is_visible_for_suppliers = models.BooleanField('Показывать в кабинетах контрагентов', default=False)
    auto_update_schedule = models.BooleanField('Автоматически обновлять услуги и дни из шаблона', default=False)

    _loaded_values = {}

    objects = TripManager()

    def natural_key(self):
        return (self.name, self.start_date) + self.agency.natural_key()

    natural_key.dependencies = ['main.agency']

    @classmethod
    def from_db(cls, db, field_names, values):
        trip = super().from_db(db, field_names, values)
        trip._loaded_values = dict(zip(field_names, values))
        return trip

    def save(self, *args, **kwargs):
        is_new = not self.pk
        super().save(*args, **kwargs)
        if not is_new and 'start_date' in self._loaded_values and \
                self.start_date != self._loaded_values['start_date']:
            self.trip_hotel_visits.all().delete()
        if not is_new:
            # Удаляем лишние записи о ночёвках
            self.trip_hotel_visits.filter(end_date__gt=self.end_date).delete()
            # Удаляем лишние записи о днях тура и о посещениях городов (ночёвки - включая день отъезда)
            self.days.filter(day__gt=self.duration_days).delete()
            from main.models.trips.schedule.abstract_trip_and_city import AbstractTripAndCity
            self.tripandcity_set.filter(day__gte=self.duration_days,
                                        objective=AbstractTripAndCity.ObjectiveEnum.OVERNIGHT).delete()
            self.tripandcity_set.filter(day__gt=self.duration_days,
                                        objective=AbstractTripAndCity.ObjectiveEnum.SIGHTSEEING).delete()
        self._loaded_values = model_to_dict(self)

    def __str__(self):
        return f"{self.start_date.strftime('%d.%m.%y')} · {self.name}"

    @property
    def duration_nights(self):
        return (self.end_date - self.start_date).days

    def start_date_time(self):
        return datetime.combine(self.start_date, self.start_time or time(00, 00))

    def end_date_time(self):
        return datetime.combine(self.end_date, self.end_time or time(00, 00))

    def is_current(self):
        """Возвращает True, если тур текущий."""
        return self.start_date <= date.today() <= self.end_date

    def is_finished(self):
        return self.end_date < date.today()

    def is_started(self):
        return self.start_date <= date.today()

    def get_date(self, day_number):
        return self.start_date + timedelta(days=max(day_number - 1, 0))

    def get_day_number(self, date):
        return (date - self.start_date).days + 1

    def days_until_start_date(self):
        return max(0, (self.start_date - date.today()).days)

    def get_today_day_number(self):
        return self.get_day_number(date.today())

    def get_city(self, day_number, objective):
        trip_and_city = self.tripandcity_set.filter(day=day_number, objective=objective).first()
        return trip_and_city.city if trip_and_city else None

    def question_message(self):
        return \
            f"""Здравствуйте!\nПишу по поводу {"экскурсии" if self.is_excursion else "тура"}: "{self.name}", """ + \
            f"""на {django_date_str(self.start_date, "«d» E")}."""

    @property
    def real_route_name(self):
        route = self.route
        return route.name if route else self.route_name

    @property
    def price_float(self):
        return float(self.price)

    def non_draft_companies(self):
        return self.trip_companies.filter(is_draft=False)

    def draft_companies(self):
        return self.trip_companies.filter(is_draft=True)

    def free_seats_count(self):
        return max(0, self.max_tourists_count - self.busy_seats_count())

    def busy_seats_count(self):
        from main.business_logic.statistics.trip_utils import annotate_tourists_count
        from main.utils.queryset_utils import get_annotated_model
        return get_annotated_model(self, annotate_queryset_fun=annotate_tourists_count).tourists_count_q

    def workers_count(self):
        return self.workers.count()

    def hotels_count(self):
        return self.hotels.count()

    def hotels_list(self):
        # TODO: как проще отсортировать по start_date?
        #TODO: переписать, нужно использовать не hotel_visit.hotel, а booking.hotel
        order_subquery = self.trip_hotel_visits.filter(hotel=models.OuterRef('pk')).values('start_date')[:1]
        ordered_hotels = self.hotels.annotate(start_date=models.Subquery(order_subquery)).distinct().\
            order_by(models.F('start_date'))
        return ordered_hotels

    def hotels_str(self):
        return '\t'.join(str(x) for x in self.hotels_list())

    def hotel_visits_ordered(self):
        return self.trip_hotel_visits.order_by('start_date')

    def get_hotel_visit(self, day_number):
        date = self.get_date(day_number)
        return self.trip_hotel_visits.filter(start_date__lte=date, end_date__gt=date).first()

    def new_hotel_visit(self, day_number):
        from main.models.trips.accommodation.trip_hotel_visit import TripHotelVisit
        start_date, end_date = self.get_new_hotel_visit_dates(day_number)
        return TripHotelVisit(trip=self, start_date=start_date, end_date=end_date)

    def get_new_hotel_visit_dates(self, day_number):
        # TODO: добавить тесты
        from main.models.trips.schedule.abstract_trip_and_city import AbstractTripAndCity
        overnight = AbstractTripAndCity.ObjectiveEnum.OVERNIGHT
        city = self.get_city(day_number, objective=overnight)
        d = day_number
        if city:
            while d > 1 and self.get_city(d - 1, objective=overnight) == city and not self.get_hotel_visit(d - 1):
                d -= 1
        start_date = self.get_date(d)
        d = day_number + 1
        if city:
            n_days = self.duration_days
            while d <= n_days and self.get_city(d, objective=overnight) == city and not self.get_hotel_visit(d):
                d += 1
        end_date = self.get_date(d)
        return start_date, end_date

    def get_old_or_new_hotel_visit_dates(self, day_number):
        old_hotel_visit = self.get_hotel_visit(day_number)
        if old_hotel_visit:
            return old_hotel_visit.start_date, old_hotel_visit.end_date
        return self.get_new_hotel_visit_dates(day_number)

    def get_tripandservice_set(self, day_number):
        """
        Возвращает отсортированный список моделей TripAndService
        (сортировка выполняется автоматически по полю order_id за счёт поля ordering в модели).
        """
        return self.tripandservice_set.filter(day=day_number)

    @property
    def guide(self):
        return self.workers.filter(role=TripWorker.RoleEnum.GUIDE).first() or \
               self.workers.filter(role=TripWorker.RoleEnum.DRIVER_GUIDE).first()

    @property
    def driver(self):
        return self.workers.filter(role=TripWorker.RoleEnum.DRIVER).first() or \
               self.workers.filter(role=TripWorker.RoleEnum.DRIVER_GUIDE).first()

    def state_display_str(self):
        return self.TripStateEnum(self.state).label if self.state else ''

    def get_services_info(self, day_number):
        info = super().get_services_info(day_number)
        info.update({
            'date': self.get_date(day_number),
        })
        hotel_visit = self.get_hotel_visit(day_number)
        if hotel_visit:
            bookings = hotel_visit.pre_bookings.all()
            info.update({
                'bookings': bookings,
                'booking_details': [{
                    'booking': x,
                    'total_amount': x.total_price(hotel_visit=hotel_visit),
                    'paid_amount': x.paid_amount_for_guide(hotel_visit=hotel_visit),
                    'remaining_amount': x.remaining_amount_for_guide(hotel_visit=hotel_visit),
                } for x in bookings],
                'hotel_visit': hotel_visit,
            })
        return info

    def get_clients_to_add(self):
        """Возвращает всех клиентов, которых можно добавить в тур."""
        exclude_pks = [x.pk for x in self.tourists.all()]
        return Client.objects.filter(agency=self.agency).exclude(pk__in=exclude_pks).\
            order_by('surname', 'name', 'middle_name')

    def get_workers_to_add(self):
        """Возвращает всех гидов и водителей, которых можно добавить в тур."""
        exclude_pks = [x.pk for x in self.workers.all()]
        return TripWorker.objects.filter(agency=self.agency).exclude(pk__in=exclude_pks).\
            order_by('role', 'surname', 'name', 'middle_name')

    def may_delete(self):
        return not self.tourists.exists() and self.confirmed_or_realized_bookings_count() == 0

    def may_edit(self):
        final_date_to_edit = self.end_date + timedelta(days=self.agency.max_days_to_edit_finished_trips)
        return final_date_to_edit >= date.today()

    def may_edit_dates(self):
        may_edit = self.may_edit()
        for hotel_visit in self.trip_hotel_visits.all():
            if hotel_visit.pre_bookings.exists():
                may_edit = False
        return may_edit

    def may_edit_schedule(self):
        return self.may_edit() and not self.auto_update_schedule

    def may_auto_update_schedule(self):
        return self.agency.is_trip_auto_update_schedule_enabled and self.auto_update_schedule and self.may_edit() \
           and not self.is_finished()

    def new_inbox_data_count(self):
        from main.models.trips.inbox_trip_company import InboxTripCompany
        return InboxTripCompany.objects.filter(trip_company__trip=self, is_archived=False).count()

    def preliminary_bookings_count(self):
        from main.models.hotels.hotel_pre_booking import HotelPreBooking
        return HotelPreBooking.objects.filter(
            trip_hotel_visits__trip=self,
            status=HotelPreBooking.BookingStatusEnum.PRELIMINARY,
        ).distinct().count()

    def confirmed_or_realized_bookings_count(self):
        from main.models.hotels.hotel_pre_booking import HotelPreBooking
        return HotelPreBooking.objects.filter(trip_hotel_visits__trip=self).\
            exclude(status=HotelPreBooking.BookingStatusEnum.PRELIMINARY).distinct().count()

    def initialize_from_route(self, route):
        """Копирует данные из шаблона при создании нового тура."""
        with transaction.atomic():
            existing_names = set(Trip.objects.filter(agency=self.agency, start_date=self.start_date).
                                 values_list('name', flat=True))
            from main.utils.utils import get_unique_name
            self.name = get_unique_name(self.name, existing_names)
            self.route = route
            self.route_name = route.name
            self.end_date = self.get_date(route.duration_days)
            self.description = route.description
            self.start_time = route.start_time
            self.end_time = route.end_time
            self.transport = route.transport
            self.save()
            self.copy_schedule_from_route(route)

    def check_may_copy_schedule_from_route(self, route):
        base_msg = "Нельзя скопировать дни и услуги из шаблона тура, так как"
        if not self.may_edit():
            return False, f"{base_msg} в тур нельзя вносить изменения."
        if self.duration_nights < route.duration_nights:
            return False, f"{base_msg} длительность тура меньше длительности, указанной в шаблоне."
        if self.duration_nights > route.duration_nights and self.trip_hotel_visits.\
                filter(end_date__gt=self.start_date + timedelta(days=self.duration_nights)).exists():
            return False, f"{base_msg} в туре уже выбраны гостиницы на дни, отсутствующие в шаблоне."
        if route != self.route and self.auto_update_schedule:
            return False, f"{base_msg} программа тура автоматически обновляется из другого шаблона."
        return True, None

    def copy_schedule_from_route(self, route):
        may_copy, error_msg = self.check_may_copy_schedule_from_route(route)
        if not may_copy:
            raise ValueError(error_msg)
        with transaction.atomic():
            self.days.all().delete()
            self.tripandcity_set.all().delete()
            self.tripandservice_set.all().delete()
            for route_day in route.days.all():
                from main.models.trips.schedule.trip_day import TripDay
                TripDay(trip=self, day=route_day.day, caption=route_day.caption).save()
            for route_and_city in route.routeandcity_set.all():
                from main.models.trips.schedule.trip_and_city import TripAndCity
                TripAndCity(trip=self, city=route_and_city.city, day=route_and_city.day,
                            objective=route_and_city.objective).save()
            for route_service in route.routeandservice_set.all():
                from main.models.trips.schedule.trip_and_service import TripAndService
                TripAndService(trip=self, day=route_service.day, service=route_service.service,
                               order_id=route_service.order_id).save()

    def get_accommodation_tabs(self):
        from main.business_logic import trip_accommodation_utils
        return trip_accommodation_utils.get_accommodation_tabs(self)

    def may_show_details_for_guide(self):
        return \
            self.end_date >= self.min_end_date_to_show_details_for_guide(self.agency) and \
            self.start_date <= self.max_start_date_to_show_details_for_guide(self.agency)

    def total_incoming_amount_for_guide(self):
        from main.models.money.payment import Payment
        from main.models.money.client_contract_expense_item import ClientContractExpenseItem
        expense_items = ClientContractExpenseItem.objects.filter(client_contract__trip_company__trip=self)
        expense_items = Payment.filter_expense_items_for_guide(expense_items, self.agency, is_outgoing=False)
        return Payment.get_expenses_sum(expense_items, is_outgoing=False)

    def total_outgoing_amount_for_guide(self):
        from main.models.money.payment import Payment
        from main.models.money.trip_service_expense_item import TripServiceExpenseItem
        from main.models.money.hotel_expense_item import HotelExpenseItem
        from main.models.money.client_contract_service_expense_item import ClientContractServiceExpenseItem
        from main.models.money.base_payment_expense_item import BasePaymentExpenseItem
        from main.models.money.guide_extra_expense_item import GuideExtraExpenseItem

        service_expense_items = TripServiceExpenseItem.objects.filter(trip_and_service__trip=self)
        hotel_expense_items = HotelExpenseItem.objects.filter(hotel_visit__trip=self)
        contract_service_expense_items = ClientContractServiceExpenseItem.objects.filter(
            contract_and_service__contract__trip_company__trip=self,
        )
        extra_expense_items = GuideExtraExpenseItem.objects.filter(payment__trip=self)
        expense_items_pks = itertools.chain(
            [x.pk for x in service_expense_items],
            [x.pk for x in hotel_expense_items],
            [x.pk for x in contract_service_expense_items],
            [x.pk for x in extra_expense_items],
        )
        all_expense_items = BasePaymentExpenseItem.objects.filter(pk__in=expense_items_pks)
        all_expense_items = Payment.filter_expense_items_for_guide(all_expense_items, self.agency, is_outgoing=True)
        return Payment.get_expenses_sum(all_expense_items, is_outgoing=True)

    def get_guide_extra_expenses_by_day(self):
        extra_expenses_by_day = []
        for day_number in self.trip_day_numbers():
            extra_expenses_by_day.append((day_number, self.get_guide_extra_expenses(day_number)))
        return OrderedDict(extra_expenses_by_day)

    def get_guide_extra_expenses(self, day_number):
        from main.models.money.payment import Payment
        from main.models.money.guide_extra_expense_item import GuideExtraExpenseItem
        expense_items = GuideExtraExpenseItem.objects.filter(payment__trip=self, day_number=day_number)
        expense_items = Payment.filter_expense_items_for_guide(expense_items, self.agency, is_outgoing=True)
        return expense_items

    def add_tourist(self, tourist, desired_room_type=None):
        # Сразу добавляем компанию для клиента (по умолчанию "сам себе компания":)
        return self.add_tourist_to_dummy_company(tourist, desired_room_type)

    def add_tourist_to_dummy_company(self, tourist, desired_room_type=None):
        if self.tourists.filter(pk=tourist.pk).exists():
            return None
        with transaction.atomic():
            from main.models.trips.tourists.trip_company import TripCompany
            company = TripCompany.objects.create(
                trip=self,
                name=TripCompany.default_company_name(tourist, self.trip_companies.all()),
            )
            if desired_room_type:
                company.desired_room_type = desired_room_type
                company.save()
            company.add_tourist(tourist)
            return company

    def add_new_tourist(self, name, surname='', sex='', date_birth=None, desired_room_type=None):
        """Вспомогательный метод для быстрого добавления нового туриста."""
        tourist = Client.objects.create(agency=self.agency, name=name, surname=surname, sex=sex, date_birth=date_birth)
        self.add_tourist(tourist, desired_room_type)
        return tourist

    def add_company_with(self, tourists, **kwargs):
        if self.tourists.filter(pk__in=[x.pk for x in tourists]).exists():
            return None
        with transaction.atomic():
            from main.models.trips.tourists.trip_company import TripCompany
            company = TripCompany.objects.create(
                trip=self,
                name=TripCompany.default_company_name(tourists[0], self.trip_companies.all()),
                **kwargs
            )
            for tourist in tourists:
                company.add_tourist(tourist)
            return company

    def add_worker(self, worker):
        self.workers.add(worker)

    def add_driver(self, name, surname='', sex='', date_birth=None):
        driver = TripWorker.create_driver(agency=self.agency, name=name, surname=surname, sex=sex,
                                          date_birth=date_birth)
        self.add_worker(driver)
        return driver

    def add_guide(self, name, surname='', sex='', date_birth=None):
        guide = TripWorker.create_guide(agency=self.agency, name=name, surname=surname, sex=sex, date_birth=date_birth)
        self.add_worker(guide)
        return guide

    def remove_company_with_tourists(self, company):
        from main.models.trips.accommodation.abstract_trip_roommates_group import AbstractTripRoommatesGroup

        for tourist in company.tourists.all():
            for group in tourist.roommate_groups.filter(trip_hotel_visit__trip=self):
                AbstractTripRoommatesGroup.remove_from_roommates_group(tourist, group)
            self.tourists.remove(tourist)
        company.delete()

    def remove_worker(self, worker):
        from main.models.trips.accommodation.abstract_trip_roommates_group import AbstractTripRoommatesGroup

        for group in worker.roommate_groups.filter(trip_hotel_visit__trip=self):
            AbstractTripRoommatesGroup.remove_from_roommates_group(worker, group)
        self.workers.remove(worker)

    @staticmethod
    def min_end_date_to_show_details_for_guide(agency):
        return date.today() - timedelta(days=agency.days_after_trip_to_show_details_for_guide)

    @staticmethod
    def max_start_date_to_show_details_for_guide(agency):
        return date.today() + timedelta(days=agency.days_before_trip_to_show_details_for_guide)

    class Meta:
        verbose_name = 'Тур'
        verbose_name_plural = 'Туры'
        constraints = [
            UniqueConstraint(fields=['agency', 'start_date', 'name'], name='%(app_label)s_%(class)s_name_is_unique'),
        ]
        permissions = [
            ('plan_trips', 'Пользователь может планировать туры (#наше)'),
            ('delete_trips', 'Пользователь может удалять туры (#наше)'),
            ('manage_trip_status', 'Пользователь может редактировать статусы туров (#наше)'),
            ('manage_trip_tourists', 'Пользователь может редактировать гостей в турах (#наше)'),
            ('manage_trip_staff', 'Пользователь может редактировать гидов/водителей в турах (#наше)'),
            ('manage_trip_accommodation', 'Пользователь может управлять расселением гостей (#наше)'),
            ('view_trip_accommodation', 'Пользователь может просматривать страницу с расселением гостей (#наше)'),
            ('print_trip_reports', 'Пользователь может печатать отчёты по туру (#наше)'),
            ('print_client_contracts', 'Пользователь может печатать туристические договоры (#наше)'),
            ('manage_money_statistics', 'Пользователь может просматривать финансовую информацию по турам (#наше)'),
        ]
