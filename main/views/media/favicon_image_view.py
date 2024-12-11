from django.http import FileResponse
from django.views import View

from main.utils.home_folder import HomeFolder
from main.views.media.logo_image_mixin import LogoImageMixin


class FaviconImageView(LogoImageMixin, View):
    default_logo_path = HomeFolder.default_folder().file_path_favicon

    def get(self, request, *args, **kwargs):
        return FileResponse(self.get_logo_stream())

    def get_logo_path(self):
        agency = self.request.user_agency
        return agency.favicon_path if agency else None
