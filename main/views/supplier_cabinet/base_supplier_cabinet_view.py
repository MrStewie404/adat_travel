from django.shortcuts import get_object_or_404
from django.urls import reverse

from main.models.services.guest_cabinet_link import GuestCabinetLink
from main.models.services.supplier_cabinet_link import SupplierCabinetLink
from main.utils.utils import decode_domain_name
from main.views.supplier_cabinet.base_supplier_or_guest_cabinet_view import BaseSupplierOrGuestCabinetView


class BaseSupplierCabinetView(BaseSupplierOrGuestCabinetView):
    """Базовый класс для всех страниц в личном кабинете контрагента."""
    _supplier = None

    @property
    def cabinet_id(self):
        return self.kwargs['cabinet_id']

    def get_supplier_cabinet_link(self):
        return get_object_or_404(SupplierCabinetLink, cabinet_id=self.cabinet_id)

    def _get_supplier(self):
        return self.get_supplier_cabinet_link().supplier

    def try_get_guest_cabinet_url(self, create_if_absent):
        supplier_cabinet = self.get_supplier_cabinet_link()
        supplier = supplier_cabinet.supplier
        if not supplier.may_have_cabinet():
            return None
        guest_cabinet = supplier_cabinet.try_get_guest_cabinet()
        if not guest_cabinet and not create_if_absent:
            return None
        if guest_cabinet:
            cabinet_id = guest_cabinet.cabinet_id
        else:
            cabinet_id = GuestCabinetLink.get_unique_cabinet_id()
            GuestCabinetLink.objects.create(supplier_cabinet=supplier_cabinet, cabinet_id=cabinet_id)
        url = self.request.build_absolute_uri(reverse('guest_lk_dashboard', args=[cabinet_id]))
        return decode_domain_name(url)
