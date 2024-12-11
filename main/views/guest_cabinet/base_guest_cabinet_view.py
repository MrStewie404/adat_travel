from django.shortcuts import get_object_or_404

from main.models.services.guest_cabinet_link import GuestCabinetLink
from main.views.supplier_cabinet.base_supplier_or_guest_cabinet_view import BaseSupplierOrGuestCabinetView


class BaseGuestCabinetView(BaseSupplierOrGuestCabinetView):
    """Базовый класс для всех страниц в кабинете для самозаписи гостей."""
    cabinet_id_url_kwarg = 'cabinet_id'

    @property
    def cabinet_id(self):
        return self.kwargs[self.cabinet_id_url_kwarg]

    def _get_supplier(self):
        return self.get_guest_cabinet_link().supplier

    def get_guest_cabinet_link(self):
        return get_object_or_404(GuestCabinetLink, cabinet_id=self.cabinet_id)

    def get_supplier_cabinet_link(self):
        return self._guest_cabinet_link.supplier_cabinet

    def dispatch(self, request, *args, **kwargs):
        self._guest_cabinet_link = self.get_guest_cabinet_link()
        return super().dispatch(request, *args, **kwargs)
