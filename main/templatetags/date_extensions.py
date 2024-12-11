from datetime import date, timedelta

from django import template

from main.utils import utils

register = template.Library()


@register.simple_tag
def today():
    return date.today()


@register.simple_tag
def tomorrow():
    return today() + timedelta(days=1)


@register.simple_tag
def yesterday():
    return today() - timedelta(days=1)


@register.filter
def is_today(value):
    if not value:
        return False
    return value == today()


@register.filter
def is_tomorrow(value):
    if not value:
        return False
    return value == tomorrow()


@register.filter
def days_until(value):
    if not value:
        return None
    return (value - today()).days


@register.filter
def natural_date(value, format=''):
    if not value:
        return ''
    if value == today():
        return 'сегодня'
    elif value == tomorrow():
        return 'завтра'
    elif value == yesterday():
        return 'вчера'
    return utils.django_date_str(value, format) if format else ''


@register.filter
def date_birth_on_or_after(value, start_date):
    """Возвращает ближайший день рождения, начиная с указанной даты."""
    if not value:
        return value
    return utils.date_birth_on_or_after(value, start_date)
