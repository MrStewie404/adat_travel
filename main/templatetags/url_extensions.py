from django import template

register = template.Library()


@register.simple_tag
def add_url_param(params_dict, key, value):
    """Добавляет новый параметр в словарь параметров."""
    dict_copy = params_dict.copy()
    dict_copy[key] = value
    return dict_copy


@register.filter
def as_absolute_url(url, request):
    return request.build_absolute_uri(url)


@register.filter
def decode_domain_name(url):
    """
    Возвращает новый url с декодированным доменным именем, которое может содержать символы Юникода
    (по умолчанию Джанго всегда кодирует url, поэтому кириллица заменяется набором латинских символов -
    ссылка получается непрезентабельная).
    """
    from main.utils import utils
    return utils.decode_domain_name(url)
