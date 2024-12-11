from main.views.supplier_cabinet.base_supplier_cabinet_view import BaseSupplierCabinetView
from main.views.supplier_cabinet.base_supplier_or_guest_future_trips_list_view import \
    BaseSupplierOrGuestFutureTripsListView


class FutureTripsListView(BaseSupplierCabinetView, BaseSupplierOrGuestFutureTripsListView):
    template_name = 'main/supplier_cabinet/future_trips.html'
