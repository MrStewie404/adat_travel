from django.db import models


class AbstractAddress(models.Model):
    """Абстрактная модель: адрес."""

    class AddressTypeEnum(models.TextChoices):
        REGISTRATION_ADDRESS = 'REGISTRATION_ADDRESS', 'Адрес регистрации'
        RESIDENTIAL_ADDRESS = 'RESIDENTIAL_ADDRESS', 'Фактический адрес (проживания)'
        LEGAL_ADDRESS = 'LEGAL_ADDRESS', 'Юридический адрес'
        DELIVERY_ADDRESS = 'DELIVERY_ADDRESS', 'Адрес доставки'

        __empty__ = '(Выберите тип адреса)'

    address = models.CharField('Адрес', max_length=512)
    address_type = models.CharField(
        'Тип адреса',
        max_length=32,
        choices=AddressTypeEnum.choices,
        blank=False
    )

    def __str__(self):
        return f"{self.address} ({self.get_address_type_display()})"

    class Meta:
        abstract = True
