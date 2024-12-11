from django.db import models
from django.db.models import UniqueConstraint

from main.models.clients.abstract_person import AbstractPerson
from main.models.clients.client import Client
from main.models.clients.person_phone_contact import PersonPhoneContact
from main.models.clients.person_registration_data import PersonRegistrationData
from main.models.clients.person_identity_document import PersonIdentityDocument


class InboxClientDataManager(models.Manager):
    def get_by_natural_key(self, is_client_exists, client__surname, client__name, client__created_at, client__agency,
                           client__middle_name, *inbox_company_args):
        from main.models.trips.inbox_trip_company import InboxTripCompany
        client = Client.objects.get_by_natural_key(
            client__surname, client__name, client__created_at, client__agency
        ) if is_client_exists else None
        kwargs = {}
        kwargs.update(
            client=client,
            inbox_trip_company=InboxTripCompany.objects.get_by_natural_key(*inbox_company_args),
        )
        if not is_client_exists:
            kwargs.update(surname=client__surname, name=client__name, middle_name=client__middle_name)
        return self.get(**kwargs)


class InboxClientData(AbstractPerson):
    """Заполненная анкета клиента турфирмы."""
    agency = None
    inbox_trip_company = models.ForeignKey('InboxTripCompany', on_delete=models.CASCADE, related_name='inbox_clients')
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='inbox_client_data_set',
                               blank=True, null=True)

    objects = InboxClientDataManager()

    def natural_key(self):
        is_client_exists = self.client is not None
        client_key = self.client.natural_key() + (None,) if is_client_exists else \
            (self.surname, self.name, None, None, self.middle_name)
        return (is_client_exists,) + client_key + self.inbox_trip_company.natural_key()

    natural_key.dependencies = ['main.client', 'main.inboxtripcompany']

    def first_self_or_client_phone_number_str(self):
        phone_number = self.first_phone_number_str()
        if not phone_number and self.client:
            phone_number = self.client.first_phone_number_str()
        return phone_number

    def copy_to_client(self):
        # TODO: написать тесты
        if not self.client:
            return
        self.client.surname = self.surname
        self.client.name = self.name
        self.client.middle_name = self.middle_name
        self.client.sex = self.sex
        self.client.date_birth = self.date_birth
        self.client.place_birth = self.place_birth
        self.client.food_preferences = self.food_preferences
        self.client.save()
        psp = self.try_get_passport()
        if psp:
            client_psp = self.client.try_get_passport()
            if not client_psp:
                client_psp = PersonIdentityDocument(person=self.client)
            client_psp.document_type = psp.document_type
            client_psp.document_series = psp.document_series
            client_psp.document_number = psp.document_number
            client_psp.issued_by = psp.issued_by
            client_psp.issue_date = psp.issue_date
            client_psp.issue_office_code = psp.issue_office_code
            client_psp.save()
        reg_data = self.try_get_registration_data()
        if reg_data:
            client_reg_data = self.client.try_get_registration_data()
            if not client_reg_data:
                client_reg_data = PersonRegistrationData(person=self.client)
            client_reg_data.address = reg_data.address
            client_reg_data.registration_date = reg_data.registration_date
            client_reg_data.save()
        phone = self.phone_numbers.first()
        if phone:
            self.client.phone_numbers.all().delete()
            PersonPhoneContact.objects.create(person=self.client, phone_type=phone.phone_type,
                                              phone_number=phone.phone_number)

    def create_client(self):
        # TODO: тоже написать тесты
        client = self.client
        if not client:
            client = Client(agency=self.inbox_trip_company.trip_company.trip.agency, name=self.name,
                            surname=self.surname, middle_name=self.middle_name, date_birth=self.date_birth)
            client.save()
            self.client = client
            self.save()
        self.copy_to_client()
        return client

    class Meta:
        verbose_name = 'Анкета клиента'
        verbose_name_plural = 'Анкеты клиентов'
        constraints = [
            UniqueConstraint(fields=['inbox_trip_company', 'client'], name='%(app_label)s_%(class)s_is_unique'),
        ]
