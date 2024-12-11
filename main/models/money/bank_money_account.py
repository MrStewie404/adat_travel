from django.db import models

from main.models.money.bank_details import BankDetails
from main.models.money.base_money_account import BaseMoneyAccount


class BankMoneyAccount(BaseMoneyAccount):
    bank = models.ForeignKey(BankDetails, on_delete=models.PROTECT, null=True, blank=True)
    bank_account = models.CharField(max_length=20, null=True, blank=True)

    @property
    def type_name(self):
        return "Безналичный"

    @property
    def type_name_prefix(self):
        return "Банк"

    @property
    def sub_title(self):
        return self.bank if self.bank else self.type_name

    @property
    def edit_url_name(self):
        return "bank_account_edit"

    @property
    def icon_name(self):
        return "icofont-bank-alt"

    class Meta:
        verbose_name = 'Денежный счёт (безналичный)'
        verbose_name_plural = 'Денежные счета (безналичные)'
