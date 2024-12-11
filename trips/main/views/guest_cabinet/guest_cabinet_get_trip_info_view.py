from main.views.guest_cabinet.base_guest_cabinet_view import BaseGuestCabinetView
from main.views.supplier_cabinet.base_supplier_or_guest_get_trip_info_view import BaseSupplierOrGuestGetTripInfoView


class GuestCabinetGetTripInfoView(BaseGuestCabinetView, BaseSupplierOrGuestGetTripInfoView):
    pass
