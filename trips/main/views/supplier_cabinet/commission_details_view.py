from datetime import date

from django.db.models.functions import Upper

from main.business_logic.statistics import supplier_utils
from main.forms.trips.list_filter import TripFilterForm
from main.utils.queryset_utils import get_annotated_model
from main.views.common.list_view_with_filter import ListViewWithFilter
from main.views.supplier_cabinet.base_supplier_cabinet_view import BaseSupplierCabinetView
from main.views.supplier_cabinet.supplier_or_guest_cabinet_context_mixin import \
    SupplierOrGuestCabinetContextMixin


class CommissionDetailsView(BaseSupplierCabinetView, SupplierOrGuestCabinetContextMixin, ListViewWithFilter):
    template_name = 'main/supplier_cabinet/commission_details.html'
    context_object_name = 'trip_companies'

    def get_page_title(self):
        return "Гости"

    def get_filter_form(self):
        return TripFilterForm(self.request, initial_state=TripFilterForm.TripFilterPresetsEnum.ALL,
                              trips_queryset=self.non_filtered_trips)

    def get_filtered_trips(self):
        return self.filter_form.filter(self.non_filtered_trips)

    def get_queryset(self):
        return self.annotated_supplier.trip_companies_list_q

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['stat_total'] = supplier_utils.get_commission_summary(self.annotated_supplier)
        context['stat_finished'] = supplier_utils.get_commission_summary(self.annotated_supplier_finished_trips)
        context['stat_non_finished'] = supplier_utils.get_commission_summary(self.annotated_supplier_non_finished_trips)
        return context

    def dispatch(self, request, *args, **kwargs):
        self.non_filtered_trips = self.get_related_trips()
        self.init_filter_search_forms()  # TODO: как избежать повторной инициализации?
        supplier = self.supplier()
        all_related_trips = self.get_filtered_trips()
        self.annotated_supplier = self.get_annotated_supplier(supplier, all_related_trips)
        self.annotated_supplier_finished_trips = self.get_annotated_supplier(
            supplier,
            all_related_trips.filter(end_date__lt=date.today()),
        )
        self.annotated_supplier_non_finished_trips = self.get_annotated_supplier(
            supplier,
            all_related_trips.filter(end_date__gte=date.today()),
        )
        return super().dispatch(request, *args, **kwargs)

    @staticmethod
    def get_annotated_supplier(supplier, related_trips):
        company_filters = dict(trip__in=related_trips, supplier=supplier)
        return get_annotated_model(
            supplier,
            lambda qs: CommissionDetailsView.annotate_related_trips_stat(qs, company_filters),
        )

    @staticmethod
    def annotate_related_trips_stat(suppliers_queryset, company_filters):
        return supplier_utils.annotate_contracts_stat(
            suppliers_queryset,
            company_filters=company_filters,
            company_order_by=('-trip__start_date', 'trip__name'),
        ).order_by(Upper('name'))
