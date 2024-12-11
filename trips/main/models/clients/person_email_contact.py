from django.db import models
from django.db.models import UniqueConstraint

from main.models.clients.abstract_email_contact import AbstractEmailContact
from main.models.clients.person import Person


class PersonEmailContactManager(models.Manager):
    def get_by_natural_key(self, email_type, email, *person_args):
        return self.get(
            email_type=email_type,
            email=email,
            person=Person.objects.get_by_natural_key(*person_args),
        )


class PersonEmailContact(AbstractEmailContact):
    """E-Mail персоны."""
    person = models.ForeignKey(Person, on_delete=models.CASCADE, related_name='emails')

    objects = PersonEmailContactManager()

    def natural_key(self):
        return (self.email_type, self.email) + self.person.natural_key()

    natural_key.dependencies = ['main.person']

    class Meta:
        verbose_name = 'E-Mail'
        verbose_name_plural = 'E-Mail-ы персональные'
        constraints = [
            UniqueConstraint(fields=['person', 'email_type', 'email'], name='%(app_label)s_%(class)s_is_unique'),
        ]
