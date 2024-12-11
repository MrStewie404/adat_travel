from django.core.exceptions import ValidationError
from django.db import models


class BankDetails(models.Model):
    """Модель для хранения реквизитов российского банка."""
    name = models.CharField(max_length=255, unique=True)
    bik = models.CharField(max_length=9, unique=True)
    correspondent_account = models.CharField(max_length=20, null=True)
    address = models.CharField(max_length=255)
    phone = models.CharField(max_length=20)

    def __str__(self):
        bik_str = f"{self.bik} · " if self.bik else ''
        return bik_str + self.name

    def clean(self):
        super().clean()

        if not self.correspondent_account.startswith('30101'):
            raise ValidationError(message='Корреспондентский счет должен начинаться с 30101')

        if not self.correspondent_account.endswith(self.bik[-3:]):
            raise ValidationError(message='Корреспондентский счет должен заканчиваться тремя последними цифрами БИК')

    class Meta:
        verbose_name = 'Банк'
        verbose_name_plural = 'Банки'
