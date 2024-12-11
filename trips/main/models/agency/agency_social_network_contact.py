from django.db import models
from django.db.models import UniqueConstraint

from main.models.agency.agency import Agency
from main.models.clients.abstract_social_network_contact import AbstractSocialNetworkContact


class AgencySocialNetworkContactManager(models.Manager):
    def get_by_natural_key(self, social_network, account, *agency_args):
        return self.get(
            social_network=social_network,
            account=account,
            person=Agency.objects.get_by_natural_key(*agency_args),
        )


class AgencySocialNetworkContact(AbstractSocialNetworkContact):
    """Аккаунт агентства в соц. сети."""
    agency = models.ForeignKey(Agency, on_delete=models.CASCADE, related_name='social_network_contacts')

    objects = AgencySocialNetworkContactManager()

    def natural_key(self):
        return (self.social_network, self.account) + self.agency.natural_key()

    natural_key.dependencies = ['main.agency']

    class Meta:
        verbose_name = 'Аккаунт агентства в соц. сети'
        verbose_name_plural = 'Аккаунты агентств в соц. сетях'
        constraints = [
            UniqueConstraint(fields=['agency', 'social_network', 'account'], name='%(app_label)s_%(class)s_is_unique'),
        ]
