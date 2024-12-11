from django.db.models import OuterRef, Count, Subquery, F, Sum
from django.db.models.functions import Coalesce, Greatest

from main.models.trips.trip import Trip
from main.models.trips.tourists.trip_company import TripCompany
from main.utils.queryset_utils import aggregate_subquery


def annotate_tourists_count(trips_queryset):
    # Все аггрегации сделаны подзапросами, чтобы обойти известный баг с JOIN-ами
    # (см. https://code.djangoproject.com/ticket/10060).
    tourists_count_subquery = aggregate_subquery(
        annotate_company_tourists_count(TripCompany.objects.filter(trip=OuterRef('pk'))),
        aggregate_fun=Sum('tourists_count_q'),
        aggregate_by='trip',
    )
    return trips_queryset.annotate(
        tourists_count_q=Coalesce(Subquery(tourists_count_subquery), 0),
    )


def annotate_company_tourists_count(companies_queryset):
    tourists_count_subquery = aggregate_subquery(
        TripCompany.objects.filter(pk=OuterRef('pk')),
        aggregate_fun=Count('tourists'),
        aggregate_by='pk',
    )
    return companies_queryset.annotate(
        contract_tourists_count_q=F('client_contract__tourists_count'),
        real_tourists_count_q=Subquery(tourists_count_subquery),
        expected_tourists_count_q=Greatest(Coalesce('expected_tourists_count', 1), 'real_tourists_count_q'),
    ).annotate(
        tourists_count_q=Coalesce('contract_tourists_count_q', 'expected_tourists_count_q')
    )


def annotate_route_name(trips_queryset):
    return trips_queryset.annotate(real_route_name_q=Coalesce('route__name', 'route_name'))
