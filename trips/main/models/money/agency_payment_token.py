from django.db import models
from django_cryptography.fields import encrypt

from main.models.agency.agency import Agency


class PaymentSystemChoicesEnum(models.IntegerChoices):
    YOOKASSA = 1, 'ЮKassa'


class AgencyPaymentToken(models.Model):
    agency = models.OneToOneField(Agency, on_delete=models.CASCADE, related_name='payment_token')
    payment_system = models.PositiveSmallIntegerField('Платёжная система', choices=PaymentSystemChoicesEnum.choices)
    account_id = models.CharField('Идентификатор магазина', max_length=128)
    secret_key = encrypt(models.CharField('Секретный ключ', max_length=128))  # TODO: Как делать ротацию ключей?

    def __str__(self):
        return self.agency.name

    class Meta:
        verbose_name = 'Ключ доступа к платёжной системе'
        verbose_name_plural = 'Ключи доступа к платёжным системам'
