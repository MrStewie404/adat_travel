from django.db import models

from main.models.clients.abstract_registration_data import AbstractRegistrationData
from main.models.clients.guest_form.inbox_client_data import InboxClientData


class InboxRegistrationDataManager(models.Manager):
    def get_by_natural_key(self, *inbox_client_data_args):
        return self.get(
            inbox_client_data=InboxClientData.objects.get_by_natural_key(*inbox_client_data_args),
        )


class InboxRegistrationData(AbstractRegistrationData):
    """Адрес и дата регистрации в анкете клиента."""
    inbox_client_data = models.OneToOneField(InboxClientData, on_delete=models.CASCADE,
                                             related_name='registration_data')

    objects = InboxRegistrationDataManager()

    def natural_key(self):
        return self.inbox_client_data.natural_key()

    natural_key.dependencies = ['main.inboxclientdata']

    class Meta:
        verbose_name = 'Адрес и дата регистрации в анкете'
        verbose_name_plural = 'Адреса и даты регистрации в анкетах клиентов'
