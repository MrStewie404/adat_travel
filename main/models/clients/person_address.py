from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import UniqueConstraint

from main.models.clients.abstract_address import AbstractAddress
from main.models.clients.person import Person


class PersonAddressManager(models.Manager):
    def get_by_natural_key(self, address_type, *person_args):
        return self.get(
            address_type=address_type,
            person=Person.objects.get_by_natural_key(*person_args),
        )


class PersonAddress(AbstractAddress):
    """Адрес персоны (кроме адреса регистрации)."""
    person = models.ForeignKey(Person, on_delete=models.CASCADE, related_name='addresses')

    objects = PersonAddressManager()

    def natural_key(self):
        return (self.address_type,) + self.person.natural_key()

    natural_key.dependencies = ['main.person']

    def clean(self):
        if self.address_type == self.AddressTypeEnum.REGISTRATION_ADDRESS:
            raise ValidationError("Эта модель не должна использоваться для адресов регистрации. "
                                  "Для этого предназначена модель PersonRegistrationData.",
                                  code='address_type_check_fail')

    class Meta:
        verbose_name = 'Адрес (кроме адреса регистрации)'
        verbose_name_plural = 'Адреса (кроме адресов регистрации)'
        constraints = [
            UniqueConstraint(fields=['person', 'address_type'], name='%(app_label)s_%(class)s_is_unique'),
        ]
