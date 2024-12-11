from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q
from django.db.models.signals import post_delete
from django.dispatch import receiver

from main.models.clients.abstract_email_contact import AbstractEmailContact
from main.models.clients.abstract_phone_contact import AbstractPhoneContact
from main.models.clients.person import Person
from main.models.services.supplier import Supplier


class PersonSupplier(Supplier):
    """Контрагент - физическое лицо."""
    supplier = models.OneToOneField(Supplier, on_delete=models.CASCADE, parent_link=True,
                                    related_name='person_supplier')
    person = models.OneToOneField(Person, on_delete=models.CASCADE, related_name='person_supplier')

    @property
    def supplier_type(self):
        return Supplier.SupplierTypeEnum.PERSON

    @property
    def address(self):
        registration_data = self.person.try_get_registration_data()
        return registration_data.address if registration_data else ''

    @property
    def phone_number(self):
        phone_model = self.person.phone_numbers.filter(phone_type=AbstractPhoneContact.default_phone_type).first()
        return phone_model.phone_number if phone_model else ''

    @property
    def email(self):
        email_model = self.person.emails.filter(email_type=AbstractEmailContact.default_email_type).first()
        return email_model.email if email_model else ''

    @property
    def social_network_contacts(self):
        return self.person.social_network_contacts

    @property
    def website(self):
        return self.person.website

    @property
    def comment(self):
        return self.person.comment

    def get_duplicate_supplier(self):
        agency = self.agency
        agency_filter = (Q(agency=None) | Q(agency=agency)) if agency else Q()
        return PersonSupplier.objects.exclude(pk=self.pk).filter(agency_filter, full_name=self.full_name).first()

    def validate_unique(self, exclude=None):
        super().validate_unique(exclude=exclude)
        duplicate_supplier = self.get_duplicate_supplier()
        if duplicate_supplier:
            raise ValidationError("Контрагент с такими ФИО уже существует", code='supplier_not_unique',
                                  params=[duplicate_supplier])

    class Meta:
        verbose_name = 'Контрагент - физическое лицо'
        verbose_name_plural = 'Контрагенты - физические лица'


@receiver(post_delete, sender='main.PersonSupplier')
def auto_delete_person(sender, instance, **kwargs):
    """Удаляет саму персону после удаления модели контрагента."""
    instance.person.delete()
