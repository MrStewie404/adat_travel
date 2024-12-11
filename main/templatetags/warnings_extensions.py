from django import template

from main.business_logic.warnings.warnings_collector import WarningsCollector

register = template.Library()


@register.filter
def safe_get(collector, key):
    """
    Этот фильтр позволяет в шаблоне получить дочерний collector.
    Например, если в шаблоне есть переменная trip, то можно её использовать как ключ: collector|safe_get:trip.
    Фильтр корректно обрабатывает ситуации, когда collector - это None или пустая строка.
    """
    default_value = WarningsCollector()
    if not collector:
        return default_value
    return collector.get_or_default(key, default_value)


@register.filter
def get_string(collector, depth=None):
    if not collector:
        return ''
    if depth is not None:
        return collector.get_string(depth=depth)
    return collector.get_string()


@register.filter
def contains_tag(collector, tag):
    if not collector:
        return False
    return tag in collector.tags


@register.simple_tag
def get_joined_keys(collector, *keys):
    if not collector:
        return WarningsCollector()
    return collector.get_joined_keys(*keys)
