from django.db import models
from django.utils import timezone

from main.models.services.supplier_cabinet_link import SupplierCabinetLink
from main.models.utils import get_unique_token


class GuestCabinetLink(models.Model):
    """Ссылка для самозаписи гостей."""
    supplier_cabinet = models.OneToOneField(SupplierCabinetLink, on_delete=models.CASCADE, related_name='guest_cabinet')
    cabinet_id = models.CharField('ID кабинета', max_length=16, unique=True)
    created_at = models.DateTimeField('Дата создания', default=timezone.now)

    def __str__(self):
        return f"{self.supplier_cabinet.supplier}: ссылка для самозаписи"

    @property
    def supplier(self):
        return self.supplier_cabinet.supplier

    @staticmethod
    def get_unique_cabinet_id():
        return get_unique_token(GuestCabinetLink, 'cabinet_id')

    class Meta:
        verbose_name = 'Ссылка для самозаписи'
        verbose_name_plural = 'Ссылки для самозаписи'
