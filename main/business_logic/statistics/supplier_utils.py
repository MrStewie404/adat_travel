from decimal import Decimal

from django.db.models import Prefetch

from main.business_logic.statistics.money.trip_money_utils import annotate_companies_contract_stat
from main.models.trips.tourists.trip_company import TripCompany


def annotate_contracts_stat(suppliers_queryset, company_filters, company_order_by=('trip__start_date', 'trip__name')):
    return suppliers_queryset.prefetch_related(
        Prefetch(
            'trip_companies',
            queryset=annotate_companies_contract_stat(
                TripCompany.objects.select_related('trip').filter(
                    supplier__isnull=False,
                    supplier_commission__gt=0,
                    **company_filters,
                )
            ).order_by(*company_order_by),
            to_attr='trip_companies_list_q',
        )
    )


def get_commission_summary(annotated_supplier):
    companies = annotated_supplier.trip_companies_list_q
    commission = sum([company.commission_q for company in companies], Decimal(0))
    commission_paid = sum([company.commission_paid_q for company in companies], Decimal(0))
    commission_remaining = sum([company.commission_remaining_q for company in companies], Decimal(0))
    tourists_count = sum([company.tourists_count_q for company in companies], 0)
    return {
        'tourists_count': tourists_count,
        'commission': commission,
        'commission_paid': commission_paid,
        'commission_remaining': commission_remaining,
    }
