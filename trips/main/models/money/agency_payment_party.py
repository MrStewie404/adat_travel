from django.db import models

from main.models.agency.agency import Agency
from main.models.money.base_payment_party import BasePaymentParty


class AgencyPaymentParty(BasePaymentParty):
    """Агентство - участник/сторона платежа."""
    payment_party = models.OneToOneField(BasePaymentParty, on_delete=models.CASCADE, parent_link=True,
                                         related_name='agency_payment_party')
    agency = models.ForeignKey(Agency, on_delete=models.SET_NULL, blank=True, null=True,
                               related_name='payment_party_links')

    @property
    def url_name(self):
        return 'supplier_dashboard'

    @property
    def url_args(self):
        return [self.agency_id]

    class Meta:
        verbose_name = 'Сторона платежа - агентство'
        verbose_name_plural = 'Стороны платежей - агентства'
