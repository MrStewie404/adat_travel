from django.db import models

from main.models.clients.person import Person
from main.models.money.base_payment_party import BasePaymentParty


class PersonPaymentParty(BasePaymentParty):
    """Человек - участник/сторона платежа (гид, клиент и т.д.)."""
    payment_party = models.OneToOneField(BasePaymentParty, on_delete=models.CASCADE, parent_link=True,
                                         related_name='person_payment_party')
    person = models.ForeignKey(Person, on_delete=models.SET_NULL, blank=True, null=True,
                               related_name='payment_party_links')

    @property
    def url_name(self):
        return 'client_dashboard'

    @property
    def url_args(self):
        return [self.person_id]

    class Meta:
        verbose_name = 'Сторона платежа - частное лицо'
        verbose_name_plural = 'Стороны платежей - частные лица'
