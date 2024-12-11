from django.views import View

from main.views.supplier_cabinet.supplier_or_guest_cabinet_mixin import SupplierOrGuestCabinetMixin


class BaseSupplierOrGuestCabinetView(SupplierOrGuestCabinetMixin, View):
    """Базовый класс для всех страниц в личном кабинете контрагента или гостя."""

    def dispatch(self, request, *args, **kwargs):
        self._init_supplier()
        return super().dispatch(request, *args, **kwargs)
