from itertools import groupby
from operator import attrgetter


def route_choices_grouped(queryset, empty_label='(Выберите шаблон)'):
    routes_grouped = groupby(queryset.order_by('duration_nights', 'name'), attrgetter('duration_days'))
    choices = [(None, empty_label)]
    for duration_days, routes in routes_grouped:
        sub_choices = [(route.pk, route.name) for route in routes]
        choices += [(f"{duration_days}-дневные туры", sub_choices)]
    return choices
