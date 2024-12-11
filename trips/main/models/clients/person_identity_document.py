from django.core.exceptions import ValidationError
from django.db import models

from main.models.clients.abstract_identity_document import AbstractIdentityDocument
from main.models.clients.person import Person


class PersonIdentityDocumentManager(models.Manager):
    def get_by_natural_key(self, document_type, *person_args):
        return self.get(
            document_type=document_type,
            person=Person.objects.get_by_natural_key(*person_args),
        )


class PersonIdentityDocument(AbstractIdentityDocument):
    """Данные о документе, удостоверяющем личность."""
    person = models.OneToOneField(Person, on_delete=models.CASCADE, related_name='passport')

    objects = PersonIdentityDocumentManager()

    def natural_key(self):
        return (self.document_type,) + self.person.natural_key()

    natural_key.dependencies = ['main.person']

    def validate_unique(self, exclude=None):
        super().validate_unique(exclude=exclude)
        agency = self.person.agency
        if PersonIdentityDocument.objects.exclude(pk=self.pk).filter(
            person__agency=agency,
            document_type=self.document_type,
            document_series=self.document_series,
            document_number=self.document_number,
        ).exists():
            raise ValidationError("Документ с такими серией и номером уже существует.", code='document_not_unique')

    class Meta:
        verbose_name = 'Удостоверение личности'
        verbose_name_plural = 'Удостоверения личности'
