from django.db import models
from django.db.models import Sum
from django.urls import reverse
from model_utils.managers import InheritanceManager

from main.models.agency.agency import Agency


class BaseMoneyAccount(models.Model):
    """Денежный счёт - позволяет привязать платёж к денежному счёту"""
    agency = models.ForeignKey(Agency, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    comment = models.TextField(blank=True, null=True)

    objects = InheritanceManager()

    def __str__(self):
        if self.type_name_prefix:
            my_list = [self.type_name_prefix, self.name]
            return ' · '.join(my_list)
        else:
            return self.name

    @property
    def dashboard_page_title(self):
        return f"{self.name}"

    @property
    def type_name(self):
        return "Неизвестно"

    @property
    def type_name_prefix(self):
        return ""

    @property
    def sub_title(self):
        return "Базовый"

    @property
    def details_url(self):
        return ""

    @property
    def edit_url_name(self):
        return ""

    @property
    def icon_name(self):
        return ""

    @property
    def edit_url(self):
        if self.edit_url_name:
            return reverse(self.edit_url_name, args=[self.pk])
        return ""

    @property
    def short_text(self):
        return self.name

    @staticmethod
    def account_choices_grouped(queryset, empty_label='(Выберите счет)'):
        acc_grouped = {}
        for acc in queryset:
            if not acc.type_name in acc_grouped:
                acc_grouped[acc.type_name] = []
            acc_grouped[acc.type_name].append(acc)

        choices = [(None, empty_label)]
        for acc_type in acc_grouped:
            acc_list = acc_grouped[acc_type]
            sub_choices = [(route.pk, route.name) for route in acc_list]
            choices += [(f"{acc_type}", sub_choices)]
        return choices

    def payments_total(self, outgoing):
        return self.get_queryset().filter(is_outgoing=outgoing).aggregate(Sum('amount'))['amount__sum'] or 0

    def get_queryset(self):
        from main.models.money.payment import Payment
        payments = Payment.objects.filter(account=self).order_by('-payment_date', 'trip')
        return payments

    def balance(self):
        amount_in = self.payments_total(False)
        amount_out = self.payments_total(True)
        return amount_in - amount_out

    class Meta:
        verbose_name = 'Денежный счёт (базовый)'
        verbose_name_plural = 'Денежные счета (базовые)'
        unique_together = ('name', 'agency')
