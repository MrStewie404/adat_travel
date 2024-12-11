from datetime import date, timedelta

from django.db import models
from django.db.models.functions import Upper
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.generic import TemplateView

from main.business_logic.statistics import supplier_utils
from main.utils.queryset_utils import get_annotated_model
from main.views.supplier_cabinet.base_supplier_cabinet_view import BaseSupplierCabinetView
from main.views.supplier_cabinet.supplier_or_guest_cabinet_context_mixin import \
    SupplierOrGuestCabinetContextMixin


@method_decorator(ensure_csrf_cookie, name='dispatch')
class DashboardView(BaseSupplierCabinetView, SupplierOrGuestCabinetContextMixin, TemplateView):
    template_name = 'main/supplier_cabinet/dashboard.html'

    def get_page_title(self):
        return self.supplier().name

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        supplier = self.supplier()
        annotated_supplier = get_annotated_model(supplier, self.annotate_current_month_stat)
        context['month_stat'] = supplier_utils.get_commission_summary(annotated_supplier)
        annotated_supplier = get_annotated_model(supplier, self.annotate_current_month_non_finished_trips_stat)
        context['month_stat_non_finished'] = supplier_utils.get_commission_summary(annotated_supplier)
        annotated_supplier = get_annotated_model(supplier, self.annotate_finished_trips_stat)
        context['finished_stat'] = supplier_utils.get_commission_summary(annotated_supplier)
        tomorrow = date.today() + timedelta(days=1)
        future_trips = self.get_future_trips()
        context['nearest_trips'] = future_trips.filter(start_date=tomorrow).exclude(end_date=models.F("start_date"))
        context['nearest_excursions'] = future_trips.filter(end_date=models.F("start_date"), start_date=tomorrow)
        context['guest_link_url'] = self.try_get_guest_cabinet_url(create_if_absent=False)
        return context

    def annotate_current_month_stat(self, suppliers_queryset):
        return supplier_utils.annotate_contracts_stat(
            suppliers_queryset,
            company_filters=dict(
                trip__agency=self.supplier().agency,
                trip__is_visible_for_suppliers=True,
                trip__start_date__gte=date.today().replace(day=1),
                trip__end_date__lt=date.today(),
            ),
        ).order_by(Upper('name'))

    def annotate_current_month_non_finished_trips_stat(self, suppliers_queryset):
        return supplier_utils.annotate_contracts_stat(
            suppliers_queryset,
            company_filters=dict(
                trip__agency=self.supplier().agency,
                trip__is_visible_for_suppliers=True,
                trip__start_date__gte=date.today().replace(day=1),
                trip__end_date__gte=date.today(),
            ),
        ).order_by(Upper('name'))

    def annotate_finished_trips_stat(self, suppliers_queryset):
        return supplier_utils.annotate_contracts_stat(
            suppliers_queryset,
            company_filters=dict(
                trip__agency=self.supplier().agency,
                trip__is_visible_for_suppliers=True,
                trip__end_date__lt=date.today(),
            ),
        ).order_by(Upper('name'))
