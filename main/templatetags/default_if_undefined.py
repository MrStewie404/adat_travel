from django import template

register = template.Library()


@register.filter
def default_if_undefined(value, default):
    """
    Иногда встроенных фильтров default и default_if_none не хватает.
    Например: в шаблоне используется булевская переменная
    и мы хотим её "инициализировать" с помощью тега with, если она не определена.
    Так как неопределённая переменная имеет значение не None, а '',
    то фильтр default_if_none тут не сработает.
    """
    return value if value != '' else default
