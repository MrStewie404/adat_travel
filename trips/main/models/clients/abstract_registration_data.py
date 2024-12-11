from django.db import models

from main.models.clients.abstract_address import AbstractAddress
from main.models.clients.person_address import PersonAddress


class AbstractRegistrationData(AbstractAddress):
    """Абстрактная модель: адрес и дата регистрации."""
    address = models.CharField('Адрес регистрации', max_length=512)
    address_type = models.CharField(
        'Тип адреса',
        max_length=32,
        default=PersonAddress.AddressTypeEnum.REGISTRATION_ADDRESS,
        editable=False
    )
    registration_date = models.DateField('Дата регистрации', blank=True, null=True)

    class Meta:
        abstract = True
