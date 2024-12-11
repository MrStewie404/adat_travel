from django.db import models
from django.db.models import UniqueConstraint

from main.models.clients.abstract_social_network_contact import AbstractSocialNetworkContact
from main.models.services.legal_supplier import LegalSupplier


class LegalSupplierSocialNetworkContactManager(models.Manager):
    def get_by_natural_key(self, social_network, account, *supplier_args):
        return self.get(
            social_network=social_network,
            account=account,
            supplier=LegalSupplier.objects.get_by_natural_key(*supplier_args),
        )


class LegalSupplierSocialNetworkContact(AbstractSocialNetworkContact):
    """Аккаунт юридического лица в соц. сети."""
    supplier = models.ForeignKey(LegalSupplier, on_delete=models.CASCADE, related_name='social_network_contacts')

    objects = LegalSupplierSocialNetworkContactManager()

    def natural_key(self):
        return (self.social_network, self.account) + self.supplier.natural_key()

    natural_key.dependencies = ['main.legalsupplier']

    class Meta:
        verbose_name = 'Аккаунт юр. лица в соц. сети'
        verbose_name_plural = 'Аккаунты юр. лиц в соц. сетях'
        constraints = [
            UniqueConstraint(fields=['supplier', 'social_network', 'account'], name='%(app_label)s_%(class)s_is_unique'),
        ]
