from django.db import models
from django.db.models import UniqueConstraint

from main.models.clients.abstract_social_network_contact import AbstractSocialNetworkContact
from main.models.clients.person import Person


class PersonSocialNetworkContactManager(models.Manager):
    def get_by_natural_key(self, social_network, account, *person_args):
        return self.get(
            social_network=social_network,
            account=account,
            person=Person.objects.get_by_natural_key(*person_args),
        )


class PersonSocialNetworkContact(AbstractSocialNetworkContact):
    """Аккаунт персоны в соц. сети."""
    person = models.ForeignKey(Person, on_delete=models.CASCADE, related_name='social_network_contacts')

    objects = PersonSocialNetworkContactManager()

    def natural_key(self):
        return (self.social_network, self.account) + self.person.natural_key()

    natural_key.dependencies = ['main.person']

    class Meta:
        verbose_name = 'Аккаунт в соц. сети'
        verbose_name_plural = 'Аккаунты в соц. сетях персональные'
        constraints = [
            UniqueConstraint(fields=['person', 'social_network', 'account'], name='%(app_label)s_%(class)s_is_unique'),
        ]
