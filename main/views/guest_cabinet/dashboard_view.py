from main.views.common.context_extensions_mixin import ContextExtensionsMixin
from main.views.guest_cabinet.base_guest_cabinet_view import BaseGuestCabinetView
from main.views.supplier_cabinet.base_supplier_or_guest_future_trips_list_view import \
    BaseSupplierOrGuestFutureTripsListView


class DashboardView(BaseGuestCabinetView, BaseSupplierOrGuestFutureTripsListView, ContextExtensionsMixin):
    template_name = 'main/guest_cabinet/dashboard.html'

    def get_page_title(self):
        return "Запись на тур"
