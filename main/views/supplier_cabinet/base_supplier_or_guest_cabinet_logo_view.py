import os

from django.http import FileResponse

from main.utils.home_folder import HomeFolder
from main.views.media.logo_image_mixin import LogoImageMixin
from main.views.supplier_cabinet.base_supplier_or_guest_cabinet_view import BaseSupplierOrGuestCabinetView


class BaseSupplierOrGuestCabinetLogoView(LogoImageMixin, BaseSupplierOrGuestCabinetView):
    default_logo_path = HomeFolder.default_folder().file_path_logo

    def get(self, request, *args, **kwargs):
        return FileResponse(self.get_logo_stream())

    def get_logo_path(self):
        agency = self.supplier().agency
        if not agency:
            return None

        path = agency.supplier_cabinet_logo_path
        if not os.path.isfile(path):
            return agency.logo_path
        return path
