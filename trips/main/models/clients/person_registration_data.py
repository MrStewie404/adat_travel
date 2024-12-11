from django.db import models

from main.models.clients.abstract_registration_data import AbstractRegistrationData
from main.models.clients.person import Person


class PersonRegistrationDataManager(models.Manager):
    def get_by_natural_key(self, *person_args):
        return self.get(
            person=Person.objects.get_by_natural_key(*person_args),
        )


class PersonRegistrationData(AbstractRegistrationData):
    """Адрес и дата регистрации."""
    person = models.OneToOneField(Person, on_delete=models.CASCADE, related_name='registration_data')

    objects = PersonRegistrationDataManager()

    def natural_key(self):
        return self.person.natural_key()

    natural_key.dependencies = ['main.person']

    class Meta:
        verbose_name = 'Адрес и дата регистрации'
        verbose_name_plural = 'Адреса и даты регистрации'
