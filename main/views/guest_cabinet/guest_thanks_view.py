from django.views.generic.detail import DetailView

from main.models.trips.tourists.client_contract.client_contract import ClientContract
from main.views.guest_cabinet.base_guest_cabinet_view import BaseGuestCabinetView
from main.views.supplier_cabinet.supplier_or_guest_cabinet_context_mixin import \
    SupplierOrGuestCabinetContextMixin


class GuestThanksView(BaseGuestCabinetView, SupplierOrGuestCabinetContextMixin, DetailView):
    model = ClientContract
    template_name = 'main/guest_cabinet/thanks.html'
    slug_url_kwarg = 'contract_slug'
    context_object_name = 'client_contract'

    def get_page_title(self):
        return "Спасибо"
