from django.db import models

from main.models.clients.person import Person
from main.models.money.base_money_account import BaseMoneyAccount


class CashMoneyAccount(BaseMoneyAccount):
    owner = models.ForeignKey(Person, on_delete=models.SET_NULL, null=True)

    @property
    def type_name(self):
        return "Наличный"

    @property
    def type_name_prefix(self):
        return "Нал"

    @property
    def sub_title(self):
        return self.owner if self.owner else self.type_name

    @property
    def edit_url_name(self):
        return "cash_account_edit"

    @property
    def icon_name(self):
        return "icofont-wallet"

    class Meta:
        verbose_name = 'Денежный счёт (для наличных расчётов)'
        verbose_name_plural = 'Денежные счета (для наличных расчётов)'
