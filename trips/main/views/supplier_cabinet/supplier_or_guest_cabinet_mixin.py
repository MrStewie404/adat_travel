from datetime import date

from django.core.exceptions import ImproperlyConfigured
from django.db import models
from django.http import Http404
from django.shortcuts import get_object_or_404

from main.business_logic.statistics.trip_utils import annotate_tourists_count
from main.models.trips.trip import Trip


class SupplierOrGuestCabinetMixin:
    """Микс-ин для всех страниц в личном кабинете контрагента или гостя."""
    _supplier = None

    def cabinet_id(self):
        raise ImproperlyConfigured("Subclasses should implement cabinet_id method")

    def supplier(self):
        if not self._supplier:
            self._supplier = self._get_supplier()
            self._check_supplier(self._supplier)
        return self._supplier

    def _get_supplier(self):
        raise ImproperlyConfigured("Subclasses should implement _get_supplier method")

    def _check_supplier(self, supplier):
        if not supplier.may_have_cabinet():
            raise Http404(f"Supplier '{supplier}' cabinet access forbidden")

    def _init_supplier(self):
        """Проверяем, что ссылка правильная и запоминаем контрагента."""
        return self.supplier()

    def get_related_trips(self):
        """Возвращает QuerySet с турами, в которых есть приглашённые контрагентом гости."""
        supplier = self.supplier()
        return Trip.objects.filter(
            agency=supplier.agency,
            is_visible_for_suppliers=True,
            trip_companies__supplier=supplier,
        ).distinct().order_by('start_date')

    def get_related_trip(self, pk):
        """
        Возвращает связанный с контрагентом тур или ошибку 404.
        """
        return get_object_or_404(self.get_related_trips(), pk=pk)

    def get_future_trips(self):
        """Возвращает QuerySet с предстоящими турами (доступными контрагенту) со свободными местами."""
        return annotate_tourists_count(Trip.objects.all()).filter(
            agency=self.supplier().agency,
            is_visible_for_suppliers=True,
            start_date__gt=date.today(),
            tourists_count_q__lt=models.F("max_tourists_count"),
        ).order_by('start_date')

    def get_future_trip(self, pk):
        """
        Возвращает предстоящий тур или ошибку 404.
        """
        return get_object_or_404(self.get_future_trips(), pk=pk)
