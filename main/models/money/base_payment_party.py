from django.db import models
from django.urls import reverse


class BasePaymentParty(models.Model):
    """Участник/сторона платежа (базовый класс для людей, контрагентов и т.д.)."""
    name = models.CharField('Имя/название', max_length=128)
    view_url = ""
    view_arg = None

    def __str__(self):
        return self.name

    @property
    def view_url(self):
        child = self.child_or_self
        if child.url_name:
            return reverse(child.url_name, args=child.url_args)
        return ""

    @property
    def url_name(self):
        return None

    @property
    def url_args(self):
        return None

    @property
    def child_or_self(self):
        return getattr(
            self,
            'person_payment_party',
            getattr(
                self,
                'agency_payment_party',
                getattr(
                    self,
                    'supplier_payment_party', self
                )
            )
        )

    class Meta:
        verbose_name = 'Участник платежа'
        verbose_name_plural = 'Участники платежей'
