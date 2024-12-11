import os

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.http import Http404, HttpResponse, FileResponse
from django.views import View


class BaseImageServeView(View):
    """
    Прокси-view для выдачи картинок путём запрашивания защищённых медиафайлов у nginx.
    См. ссылки: https://b0uh.github.io/protect-django-media-files-per-user-basis-with-nginx.html
    https://www.nginx.com/resources/wiki/start/topics/examples/xsendfile/
    https://stackoverflow.com/questions/45872539/django-and-nginx-x-accel-redirect
    """

    def get_image(self):
        raise ImproperlyConfigured("BaseImageServeView requires a definition of 'get_image'")

    def get(self, request, *args, **kwargs):
        self.image = self.get_image()
        if not self.image or not os.path.isfile(self.image.path):
            raise Http404
        if settings.DEBUG:
            return FileResponse(open(self.image.path, 'rb'))
        response = HttpResponse(status=200)
        # Тип содержимого будет определён nginx
        del response['Content-Type']
        response['X-Accel-Redirect'] = self.image.url
        return response
