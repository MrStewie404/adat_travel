from django.conf import settings
from django.http import HttpResponseNotFound, HttpResponseForbidden
from django.shortcuts import render


# Залипуха для режима DEBUG, вдруг пригодится.
# Показываем наши страницы об ошибках вместо жёлтого окошка Django, чтобы не "светить" подробности про сайт.
# Чтобы включить залипуху, достаточно добавить этот класс в список middleware.
class ExceptionHookMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        if settings.DEBUG and 400 <= response.status_code < 600:
            if response.status_code == HttpResponseNotFound.status_code:
                page = '404.html'
            elif response.status_code == HttpResponseForbidden.status_code:
                page = '403.html'
            else:
                page = '500.html'
            return render(request, page, status=response.status_code)
        return response
