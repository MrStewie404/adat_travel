from django.shortcuts import get_object_or_404

from main.business_logic.statistics.route_utils import annotate_min_max_price
from main.models.routes.route import Route
from main.views.supplier_cabinet.base_supplier_or_guest_cabinet_view import BaseSupplierOrGuestCabinetView


class BaseSupplierOrGuestTripBookingView(BaseSupplierOrGuestCabinetView):
    route_pk_url_kwarg = 'route_pk'

    def dispatch(self, request, *args, **kwargs):
        self.future_trips = self.get_future_trips()
        self.route = self.get_route()
        self.route_trips = self.future_trips.filter(route=self.route).order_by('start_date')
        return super().dispatch(request, *args, **kwargs)

    @property
    def route_pk(self):
        return self.kwargs[self.route_pk_url_kwarg]

    def get_route(self):
        routes = Route.objects.filter(trips__in=self.future_trips).distinct()
        routes = annotate_min_max_price(routes)
        return get_object_or_404(routes, pk=self.route_pk)

    def min_trip_price(self):
        return self.route.min_price_q

    def has_different_prices(self):
        return len(self.route_trips.values('price').order_by()) > 1
