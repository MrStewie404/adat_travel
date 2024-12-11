from django.db import models

from main.models.clients.abstract_contact import AbstractContact


class AbstractPhoneContact(AbstractContact):
    """Абстрактная модель: телефон для связи."""

    class PhoneTypeEnum(models.TextChoices):
        WORK = 'WORK', 'Рабочий'
        MOBILE = 'MOBILE', 'Мобильный'
        HOME = 'HOME', 'Домашний'
        PAGER = 'PAGER', 'Пейджер'
        FAX = 'FAX', 'Факс'
        OTHER = 'OTHER', 'Другой'

        __empty__ = '(Выберите тип номера)'

    default_phone_type = PhoneTypeEnum.MOBILE

    phone_number = models.CharField('Телефон', max_length=32)
    phone_type = models.CharField(
        'Тип номера',
        max_length=16,
        choices=PhoneTypeEnum.choices,
        blank=False
    )

    def __str__(self):
        return f"{self.phone_number_formatted} ({self.get_phone_type_display()})"

    @property
    def phone_number_formatted(self):
        from main.templatetags import format_extensions
        return format_extensions.phonenumber(self.phone_number)

    class Meta:
        abstract = True
