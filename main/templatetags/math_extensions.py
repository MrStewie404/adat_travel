from typing import SupportsAbs

from django import template

register = template.Library()


@register.filter(name="abs", is_safe=False)
def abs_filter(value):
    """Возвращает абсолютное значение аргумента."""
    if isinstance(value, SupportsAbs):
        return abs(value)
    return None


@register.filter(name="min", is_safe=False)
def min_filter(value1, value2):
    """Возвращает минимальное значение."""
    if value1 is None or value1 == '' or value2 is None or value2 == '':
        return None
    return min(value1, value2)


@register.filter(name="max", is_safe=False)
def max_filter(value1, value2):
    """Возвращает минимальное значение."""
    if value1 is None or value1 == '' or value2 is None or value2 == '':
        return None
    return max(value1, value2)


@register.filter(name="minus", is_safe=False)
def minus_filter(value1, value2):
    """Возвращает разницу двух чисел."""
    if not hasattr(value1, '__sub__') or not hasattr(value2, '__sub__'):
        return None
    return value1 - value2
