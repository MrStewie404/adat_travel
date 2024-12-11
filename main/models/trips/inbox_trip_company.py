from datetime import date

from django.db import models
from django.utils import timezone

from main.models.trips.tourists.trip_company import TripCompany


class InboxTripCompanyManager(models.Manager):
    def get_by_natural_key(self, *trip_company_args):
        return self.get(trip_company=TripCompany.objects.get_by_natural_key(*trip_company_args))


class InboxTripCompany(models.Model):
    """Заполненная анкета на компанию туристов."""
    trip_company = models.OneToOneField(TripCompany, on_delete=models.CASCADE, related_name='inbox_trip_company')
    created_at = models.DateTimeField('Дата создания', default=timezone.now)
    modified_at = models.DateTimeField('Дата изменения', default=timezone.now)
    is_archived = models.BooleanField('Архив', default=False)

    objects = InboxTripCompanyManager()

    def natural_key(self):
        return self.trip_company.natural_key()

    natural_key.dependencies = ['main.tripcompany']

    def __str__(self):
        return str(self.trip_company)

    def copy_to_trip_company(self):
        # TODO: написать тесты
        for inbox_client in self.inbox_clients.all():
            if inbox_client.client:
                inbox_client.copy_to_client()
            else:
                client = inbox_client.create_client()
                self.trip_company.add_tourist(client)
                for company in self.extra_companies_to_copy_to():
                    company.add_tourist(client)

    def extra_companies_to_copy_to(self):
        return TripCompany.objects.filter(
            trip__agency=self.trip_company.trip.agency,
            trip__start_date__gte=date.today(),
            tourists=self.trip_company.get_customer(),
        ).exclude(pk=self.trip_company.pk).distinct()

    class Meta:
        verbose_name = 'Анкета на компанию туристов'
        verbose_name_plural = 'Анкеты на компании туристов'
