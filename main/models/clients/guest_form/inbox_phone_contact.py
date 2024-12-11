from django.db import models

from main.models.clients.abstract_phone_contact import AbstractPhoneContact
from main.models.clients.guest_form.inbox_client_data import InboxClientData


class InboxPhoneContactManager(models.Manager):
    def get_by_natural_key(self, phone_number, phone_type, *inbox_client_data_args):
        return self.get(
            phone_number=phone_number,
            phone_type=phone_type,
            inbox_client_data=InboxClientData.objects.get_by_natural_key(*inbox_client_data_args),
        )


class InboxPhoneContact(AbstractPhoneContact):
    """Номер телефона в анкете клиента."""
    inbox_client_data = models.ForeignKey(InboxClientData, on_delete=models.CASCADE, related_name='phone_numbers')

    objects = InboxPhoneContactManager()

    def natural_key(self):
        return (self.phone_number, self.phone_type) + self.inbox_client_data.natural_key()

    natural_key.dependencies = ['main.inboxclientdata']

    class Meta:
        verbose_name = 'Телефон в анкете'
        verbose_name_plural = 'Телефоны в анкетах клиентов'
