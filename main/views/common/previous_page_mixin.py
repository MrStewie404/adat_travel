from django.contrib.auth.views import SuccessURLAllowedHostsMixin
from django.utils.http import url_has_allowed_host_and_scheme


class PreviousPageMixin(SuccessURLAllowedHostsMixin):
    prev_field_name = 'prev'

    def get_previous_url(self):
        """
        Возвращает ссылку на предыдущую страницу из параметров GET-запроса, если эта ссылка безопасна
        (см. django.contrib.auth.LoginView).
        """
        url = self.request.GET.get(self.prev_field_name, '')
        return self.process_redirect_url(url)

    def process_redirect_url(self, url):
        url_is_safe = url_has_allowed_host_and_scheme(
            url=url,
            allowed_hosts=self.get_success_url_allowed_hosts(),
            require_https=self.request.is_secure(),
        )
        return url if url_is_safe else ''
