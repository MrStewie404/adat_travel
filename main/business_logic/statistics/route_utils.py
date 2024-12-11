from decimal import Decimal

from django.db.models import OuterRef, Min, Subquery, Max
from django.db.models.functions import Coalesce

from main.utils.queryset_utils import aggregate_subquery


def annotate_min_max_price(routes_queryset):
    min_price_subquery = aggregate_subquery(
        routes_queryset.filter(pk=OuterRef('pk')),
        aggregate_fun=Min('trips__price'),
        aggregate_by='pk',
    )
    max_price_subquery = aggregate_subquery(
        routes_queryset.filter(pk=OuterRef('pk')),
        aggregate_fun=Max('trips__price'),
        aggregate_by='pk',
    )
    return routes_queryset.annotate(
        min_price_q=Coalesce(Subquery(min_price_subquery), Decimal(0)),
        max_price_q=Coalesce(Subquery(max_price_subquery), Decimal(0)),
    )
