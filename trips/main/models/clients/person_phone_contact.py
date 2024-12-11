from django.db import models
from django.db.models import UniqueConstraint

from main.models.clients.abstract_phone_contact import AbstractPhoneContact
from main.models.clients.person import Person


class PersonPhoneContactManager(models.Manager):
    def get_by_natural_key(self, phone_number, phone_type, *person_args):
        return self.get(
            phone_number=phone_number,
            phone_type=phone_type,
            person=Person.objects.get_by_natural_key(*person_args),
        )


class PersonPhoneContact(AbstractPhoneContact):
    """Телефон для связи."""
    person = models.ForeignKey(Person, on_delete=models.CASCADE, related_name='phone_numbers')

    objects = PersonPhoneContactManager()

    def natural_key(self):
        return (self.phone_number, self.phone_type) + self.person.natural_key()

    natural_key.dependencies = ['main.person']

    class Meta:
        verbose_name = 'Телефон'
        verbose_name_plural = 'Телефоны персональные'
        constraints = [
            UniqueConstraint(fields=['person', 'phone_type', 'phone_number'], name='%(app_label)s_%(class)s_is_unique'),
        ]
