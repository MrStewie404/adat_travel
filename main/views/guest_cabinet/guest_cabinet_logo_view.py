from main.views.guest_cabinet.base_guest_cabinet_view import BaseGuestCabinetView
from main.views.supplier_cabinet.base_supplier_or_guest_cabinet_logo_view import BaseSupplierOrGuestCabinetLogoView


class GuestCabinetLogoView(BaseGuestCabinetView, BaseSupplierOrGuestCabinetLogoView):
    pass
