from django.db import models
from django.utils import timezone

from main.models.services.supplier import Supplier
from main.models.utils import get_unique_token


class SupplierCabinetLink(models.Model):
    """Ссылка на личный кабинет контрагента."""
    supplier = models.OneToOneField(Supplier, on_delete=models.CASCADE, related_name='supplier_cabinet')
    cabinet_id = models.CharField('ID кабинета', max_length=16, unique=True)
    created_at = models.DateTimeField('Дата создания', default=timezone.now)

    def __str__(self):
        return f"{self.supplier}: личный кабинет"

    def try_get_guest_cabinet(self):
        return getattr(self, "guest_cabinet", None)

    @staticmethod
    def get_unique_cabinet_id():
        return get_unique_token(SupplierCabinetLink, 'cabinet_id')

    class Meta:
        verbose_name = 'Ссылка на личный кабинет контрагента'
        verbose_name_plural = 'Ссылки на личные кабинеты контрагентов'
