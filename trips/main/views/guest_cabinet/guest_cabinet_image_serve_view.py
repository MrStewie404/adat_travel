from main.views.guest_cabinet.base_guest_cabinet_view import BaseGuestCabinetView
from main.views.media.simple_image_serve_view import SimpleImageServeView


class GuestCabinetImageServeView(SimpleImageServeView, BaseGuestCabinetView):
    pass
