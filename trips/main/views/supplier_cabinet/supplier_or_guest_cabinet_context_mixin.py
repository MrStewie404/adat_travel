import os

from main.views.common.context_extensions_mixin import ContextExtensionsMixin
from main.views.supplier_cabinet.supplier_or_guest_cabinet_mixin import SupplierOrGuestCabinetMixin


class SupplierOrGuestCabinetContextMixin(ContextExtensionsMixin, SupplierOrGuestCabinetMixin):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        supplier = self.supplier()
        agency = supplier.agency
        context['cabinet_id'] = self.cabinet_id
        context['supplier'] = supplier
        navbar_theme = 'light' if agency and os.path.isfile(agency.supplier_cabinet_navbar_theme_light_path) else 'dark'
        context['navbar_theme'] = navbar_theme
        return context
