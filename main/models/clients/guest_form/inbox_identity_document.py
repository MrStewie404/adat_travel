from django.db import models

from main.models.clients.abstract_identity_document import AbstractIdentityDocument
from main.models.clients.guest_form.inbox_client_data import InboxClientData


class InboxIdentityDocumentManager(models.Manager):
    def get_by_natural_key(self, document_type, *inbox_client_data_args):
        return self.get(
            document_type=document_type,
            inbox_client_data=InboxClientData.objects.get_by_natural_key(*inbox_client_data_args),
        )


class InboxIdentityDocument(AbstractIdentityDocument):
    """Данные о документе, удостоверяющем личность, в анкете клиента."""
    inbox_client_data = models.OneToOneField(InboxClientData, on_delete=models.CASCADE, related_name='passport')

    objects = InboxIdentityDocumentManager()

    def natural_key(self):
        return (self.document_type,) + self.inbox_client_data.natural_key()

    natural_key.dependencies = ['main.inboxclientdata']

    class Meta:
        verbose_name = 'Удостоверение личности в анкете'
        verbose_name_plural = 'Удостоверения личности в анкетах клиентов'
