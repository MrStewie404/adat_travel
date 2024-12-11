from django.db import models
from django.db.models import Q, Prefetch, ExpressionWrapper, BooleanField
from django.views.generic import ListView

from main.business_logic.statistics.route_utils import annotate_min_max_price
from main.models.routes.route import Route
from main.models.workers.trip_worker import TripWorker
from main.views.supplier_cabinet.base_supplier_or_guest_cabinet_view import BaseSupplierOrGuestCabinetView
from main.views.supplier_cabinet.supplier_or_guest_cabinet_context_mixin import \
    SupplierOrGuestCabinetContextMixin


class BaseSupplierOrGuestFutureTripsListView(BaseSupplierOrGuestCabinetView, SupplierOrGuestCabinetContextMixin, ListView):
    show_excursions = True
    show_trips = True
    context_object_name = 'trip_templates'

    def dispatch(self, request, *args, **kwargs):
        self.non_filtered_trips = self.get_non_filtered_trips()
        return super().dispatch(request, *args, **kwargs)

    def get_page_title(self):
        return "Экскурсии" if self.show_excursions and not self.show_trips else "Туры"

    def get_queryset(self):
        trips = self.non_filtered_trips
        routes = Route.objects.filter(trips__in=trips).distinct().order_by('name').prefetch_related(
            Prefetch(
                'trips',
                queryset=trips.prefetch_related(
                    Prefetch(
                        'workers',
                        queryset=TripWorker.objects.filter(
                            Q(role=TripWorker.RoleEnum.GUIDE) | Q(role=TripWorker.RoleEnum.DRIVER_GUIDE)
                        ).annotate(
                            is_guide_q=ExpressionWrapper(
                                Q(role=TripWorker.RoleEnum.GUIDE),
                                output_field=BooleanField()
                            )
                        ).order_by('-is_guide_q'),
                        to_attr='guide_list_q',
                    )
                ),
                to_attr='trip_list_q',
            )
        )
        return annotate_min_max_price(routes)

    def get_non_filtered_trips(self):
        trips = self.get_future_trips()
        if not self.show_trips:
            trips = trips.filter(end_date=models.F('start_date'))
        if not self.show_excursions:
            trips = trips.exclude(end_date=models.F('start_date'))
        return trips.select_related('route')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['show_excursions'] = self.show_excursions
        context['show_trips'] = self.show_trips
        context['week_days_info'] = self.get_week_days_info(self.object_list, self.non_filtered_trips)
        return context

    @staticmethod
    def get_week_days_info(routes, non_filtered_trips):
        info_by_route_pk = {}
        for route in routes:
            week_info = []
            for i, name in enumerate(['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Вс'], 0):
                week_info.append({
                    'weekday_ind': i,
                    'weekday_name': name,
                    'exists': any(trip.route == route and trip.start_date.weekday() == i for trip in non_filtered_trips),
                })
            info_by_route_pk[route.pk] = week_info
        return info_by_route_pk
