from django.core.exceptions import ImproperlyConfigured

from main.utils.utils import is_valid_image


class LogoImageMixin:
    default_logo_path = None

    def get_logo_stream(self):
        selected_path = self.get_valid_logo_path()
        return open(selected_path, 'rb') if selected_path else ()

    def get_valid_logo_path(self):
        logo_paths = (self.get_logo_path(), self.get_default_logo_path())
        selected_path = ''
        for path in logo_paths:
            if not selected_path and self.check_valid_image(path):
                selected_path = path
        return selected_path

    def get_logo_path(self):
        return None

    def get_default_logo_path(self):
        if self.default_logo_path is None:
            raise ImproperlyConfigured(
                    "LogoImageMixin requires either a definition of "
                    "'default_logo_path' or an implementation of 'get_default_logo_path()'"
                )
        return self.default_logo_path

    def check_valid_image(self, logo_path):
        # Легковесная проверка, что логотип - это действительно картинка, причём с разумным количеством пискелей
        # (какая-то проверка нужна, т.к. логотипы подкладываются вручную)
        return logo_path and is_valid_image(logo_path, check_loadable=False)
