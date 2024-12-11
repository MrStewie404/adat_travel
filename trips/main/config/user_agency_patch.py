from django.http import HttpRequest

from main.models.agency.agency_employee import AgencyEmployee


def get_agency(request):
    if not hasattr(request, '_cached_user_agency'):
        request._cached_user_agency = AgencyEmployee.get_agency(request.user)
    return request._cached_user_agency


def install_user_agency_patch():
    """
    Добавляет свойство user_agency в HttpRequest
    (через Middleware получается плохо: чтобы вызов get_agency был "ленивым", его надо обернуть в SimpleLazyObject,
    но при этом можно получить загадочную ошибку, если get_agency вернёт None,
    а мы попытаемся использовать этот "обёрнутый" None в функции QuerySet.filter).
    """
    HttpRequest.user_agency = property(lambda request: get_agency(request))
