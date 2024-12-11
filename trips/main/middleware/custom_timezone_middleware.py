import pytz

from django.utils import timezone


class CustomTimezoneMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # tzname = request.session.get('django_timezone')
        # if tzname:
        #     timezone.activate(pytz.timezone(tzname))
        # else:
        #     timezone.deactivate()

        # Задаём московское время для ввода/вывода времён на сайте
        # См. https://docs.djangoproject.com/en/3.2/topics/i18n/timezones/#default-time-zone-and-current-time-zone
        timezone.activate(pytz.timezone('Europe/Moscow'))
        return self.get_response(request)
