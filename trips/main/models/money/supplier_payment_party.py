from django.db import models

from main.models.money.base_payment_party import BasePaymentParty
from main.models.services.supplier import Supplier


class SupplierPaymentParty(BasePaymentParty):
    """Контрагент - участник/сторона платежа."""
    payment_party = models.OneToOneField(BasePaymentParty, on_delete=models.CASCADE, parent_link=True,
                                         related_name='supplier_payment_party')
    supplier = models.ForeignKey(Supplier, on_delete=models.SET_NULL, blank=True, null=True,
                                 related_name='payment_party_links')

    @property
    def url_name(self):
        return 'supplier_dashboard'

    @property
    def url_args(self):
        return [self.supplier_id]

    class Meta:
        verbose_name = 'Сторона платежа - контрагент'
        verbose_name_plural = 'Стороны платежей - контрагенты'
