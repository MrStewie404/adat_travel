import datetime

from django.db import models
from django.forms import Form, ChoiceField, MultipleChoiceField

from main.forms.common.date_filter_form_mixin import DateFilterFormMixin
from main.forms.common.widgets import select, rich_select
from main.forms.routes.route_choices_grouped import route_choices_grouped
from main.models.routes.route import Route
from main.models.trips.trip import Trip
from main.utils.utils import int_or_default


class TripFilterForm(DateFilterFormMixin, Form):

    class TripFilterPresetsEnum(models.TextChoices):
        ALL = 'ALL', 'Все туры'
        ACTIVE = 'ACTIVE', 'Активные туры'
        ARCHIVE = 'ARCHIVE', 'Архив туров'
        NEXT_10_DAYS = 'NEXT_10_DAYS', 'Туры в ближайшие 10 дней'
        NEXT_5_DAYS = 'NEXT_5_DAYS', 'Туры в ближайшие 5 дней'
        CURRENT = 'CURRENT', 'Текущие туры'
        ANALYTICS = 'ANALYTICS', 'Аналитика'

        @property
        def days(self):
            if self == self.NEXT_10_DAYS:
                return 10
            if self == self.NEXT_5_DAYS:
                return 5
            return 0

    default_raw_state = TripFilterPresetsEnum.ACTIVE
    need_group_route_choices = True

    route = ChoiceField(
        choices=(),
        widget=rich_select('', css_class='js-select2-larger'),
        label='',
        required=False,
    )
    state = ChoiceField(
        choices=TripFilterPresetsEnum.choices,
        widget=select(),
        label='',
    )
    days_count = MultipleChoiceField(
        choices=[(i, str(i)) for i in range(1, 10 + 1)],
        widget=rich_select('   (Любое)', css_class='js-multi-select2', multiple=True, width="100%"),
        label='',
        required=False,
    )

    agency = None
    trips_queryset = None

    def __init__(self, request, initial_state=TripFilterPresetsEnum.ACTIVE, trips_queryset=None):
        self.default_raw_state = initial_state
        self.agency = request.user_agency
        self.trips_queryset = trips_queryset if trips_queryset is not None else Trip.objects.filter(agency=self.agency)
        self.use_dates_filter = True
        if not list(request.GET.items()):
            super().__init__(initial={'state': initial_state.value})
        else:
            super().__init__(data=request.GET)
        self.fields['route'].choices = self.route_choices()

    def route_choices(self):
        routes = self.route_queryset()
        if self.need_group_route_choices:
            values = route_choices_grouped(routes, empty_label='(Все)')
        else:
            values = [(None, '(Все)')] + [(route.pk, route.name) for route in routes]
        return values

    def route_queryset(self):
        return Route.objects.filter(agency=self.agency, trips__in=self.trips_queryset).distinct().order_by('name')

    @property
    def use_filter_by_end_date_instead_start_date(self):
        return self.raw_state() in [self.TripFilterPresetsEnum.ACTIVE,
                                    self.TripFilterPresetsEnum.CURRENT,
                                    self.TripFilterPresetsEnum.ARCHIVE,
                                    self.TripFilterPresetsEnum.ANALYTICS]

    @property
    def first_date_filter(self):
        if self.raw_state() in [self.TripFilterPresetsEnum.ACTIVE,
                                self.TripFilterPresetsEnum.CURRENT,
                                self.TripFilterPresetsEnum.NEXT_5_DAYS,
                                self.TripFilterPresetsEnum.NEXT_10_DAYS]:
            return datetime.date.today()
        trips = self.trips_queryset
        if trips.exists():
            return trips.earliest('start_date').start_date
        return datetime.date.today()  # Если туров ещё нет, берём текущую дату

    @property
    def last_date_filter(self):
        state = self.raw_state()
        if state and state.days > 0:
            return datetime.date.today() + datetime.timedelta(days=state.days)
        trips = self.trips_queryset
        if trips.exists():
            if self.use_filter_by_end_date_instead_start_date:
                last_date_from_db = trips.latest('end_date').end_date
            else:
                last_date_from_db = trips.latest('start_date').start_date
            if state == self.TripFilterPresetsEnum.ARCHIVE:
                return min(datetime.date.today(), last_date_from_db)
            if state == self.TripFilterPresetsEnum.ANALYTICS:
                return min(datetime.date.today(), last_date_from_db)
        else:
            last_date_from_db = datetime.date.today()  # Если туров ещё нет, берём текущую дату
        return last_date_from_db

    def clean_route(self):
        return self.validate_and_clean('route')

    def clean_days_count(self):
        count_list = []
        strings_list = self.validate_and_clean('days_count') or []
        for x in strings_list:
            i = int_or_default(x)
            if i:
                count_list.append(i)
        return count_list

    def raw_state(self):
        # в этом методе не надо вызывать is_valid так как он чистит форму раньше её формирования
        state_value = self.data['state'] if 'state' in self.data.keys() else None
        if state_value in self.TripFilterPresetsEnum.values:
            return self.TripFilterPresetsEnum(state_value)
        return self.default_raw_state

    def active_sidebar_item(self):
        return f"TRIPS_{self.raw_state()}"

    def filter_by_route(self, query_set):
        route = self.clean_route()
        if route:
            return query_set.filter(route__exact=route)
        return query_set

    def filter_by_days_count(self, query_set):
        count_list = self.clean_days_count()
        if count_list:
            return query_set.annotate(duration=models.F('end_date') - models.F('start_date')).\
                filter(duration__in=[datetime.timedelta(days=x - 1) for x in count_list])
        return query_set

    def filter(self, query_set):
        if self.use_filter_by_end_date_instead_start_date:
            date_field_name_for_first_last_date = 'end_date'
        else:
            date_field_name_for_first_last_date = 'start_date'
        query_set = self.do_filter_by_month(query_set, month_str=self.clean_month(),
                                            date_field_name='start_date',
                                            date_field_name_for_first_last_date=date_field_name_for_first_last_date)
        if self.raw_state() == self.TripFilterPresetsEnum.CURRENT:
            query_set = query_set.annotate(tourists_count=models.Count('tourists')).\
                filter(start_date__lte=datetime.date.today(), tourists_count__gt=0)
        query_set = self.filter_by_route(query_set)
        query_set = self.filter_by_days_count(query_set)
        return query_set
