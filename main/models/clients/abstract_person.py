from datetime import date

from django.db import models
from django.db.models.functions import Concat, Trim

from main.models.agency.agency import Agency


class BasePersonManager(models.Manager):
    def get_by_natural_key(self, surname, name, created_at, agency__name):
        kwargs = {}
        kwargs.update(
            surname=surname,
            name=name,
            agency=Agency.objects.get_by_natural_key(agency__name),
        )
        if created_at:
            kwargs.update(created_at=created_at)
        return self.get(**kwargs)


class AbstractPerson(models.Model):
    """Абстрактная модель: персональные данные."""

    class SexEnum(models.TextChoices):
        MALE = 'M', 'м'
        FEMALE = 'F', 'ж'

        __empty__ = '(Выберите пол)'

    # Тут не надо использовать атрибут related_name, т.к. это у нас абстрактная модель.
    # См. https://docs.djangoproject.com/en/3.2/topics/db/models/#be-careful-with-related-name-and-related-query-name
    agency = models.ForeignKey(Agency, on_delete=models.CASCADE)
    form_of_address = models.CharField("Форма обращения", max_length=16, blank=True)
    surname = models.CharField('Фамилия', max_length=32, blank=True)
    name = models.CharField('Имя', max_length=32)
    middle_name = models.CharField('Отчество', max_length=32, blank=True)
    sex = models.CharField(
        'Пол',
        max_length=1,
        choices=SexEnum.choices,
        blank=True,
    )
    date_birth = models.DateField('Дата рождения', blank=True, null=True)
    place_birth = models.CharField('Место рождения', max_length=256, blank=True)
    website = models.URLField('Web-сайт', blank=True)
    food_preferences = models.TextField('Предпочтения по питанию', blank=True)
    comment = models.TextField('Комментарий', blank=True)

    objects = BasePersonManager()

    def natural_key(self):
        created_at = getattr(self, 'created_at', None)
        return (self.surname, self.name, created_at) + self.agency.natural_key()

    natural_key.dependencies = ['main.agency']

    def __str__(self):
        return self.full_name()

    def full_name(self):
        return f"{self.surname} {self.name} {self.middle_name}".strip()

    def signature_initials(self):
        if not self.surname:
            return self.name
        middle_name_part = f"{self.middle_name[0]}." if self.middle_name else ''
        return f"{self.surname} {self.name[0]}.{middle_name_part}"

    def signature_initials_for_filename(self):
        if not self.surname:
            return self.name
        return f"{self.surname}_{self.name[0]}{self.middle_name[0] if self.middle_name else ''}"

    def age(self):
        today = date.today()
        date_birth = self.date_birth if self.date_birth else today
        return today.year - date_birth.year - ((today.month, today.day) < (date_birth.month, date_birth.day))

    def age_str(self):
        if not self.date_birth:
            return '-'
        return str(self.age())

    def date_birth_str(self):
        if self.date_birth:
            return self.date_birth.strftime('%d.%m.%Y')
        return ''

    def date_birth_in_trip(self, trip):
        if not self.date_birth:
            return None
        from main.utils import utils
        date_birth = utils.date_birth_on_or_after(self.date_birth, trip.start_date)
        if date_birth > trip.end_date:
            return None
        return date_birth

    def phone_numbers_list(self):
        return self.phone_numbers.all()

    def phone_numbers_str(self, with_phone_types=True):
        phones = list(self.phone_numbers.all())
        if len(phones) == 1:
            return phones[0].phone_number  # В этом случае не печатаем тип номера
        return '\n'.join(str(x) if with_phone_types else x.phone_number_formatted for x in phones)

    def first_phone_number_str(self):
        phone = self.phone_numbers.first()
        if not phone:
            return ''
        return phone.phone_number_formatted

    def full_comment(self):
        comment = self.comment
        if self.food_preferences:
            food_comment = f"Питание: {self.food_preferences}"
            return f"{comment}\n{food_comment}" if comment else food_comment
        return comment

    def try_get_passport(self):
        return getattr(self, 'passport', None)

    def passport_number_str(self):
        return self.passport_do(lambda p: f"{p.document_series} {p.document_number}".strip(), if_none="")

    def passport_do(self, action, if_none=None):
        passport = self.try_get_passport()
        if not passport:
            return if_none
        return action(passport)

    def passport_full_str_rus(self):
        passport = self.try_get_passport()
        if not passport:
            return ""
        issued_by_str = ''
        office_code_str = ''
        if passport.issued_by:
            issued_by_str = f", выдан {passport.issued_by}" \
                            f" {passport.issue_date.strftime('%d.%m.%Y') if passport.issue_date else ''}"
        if passport.issue_office_code:
            office_code_str = f", код подразделения {passport.issue_office_code}"
        return f"{passport.document_type_str()} {passport.document_series} {passport.document_number}" \
               f"{issued_by_str}{office_code_str}"

    def try_get_registration_data(self):
        return getattr(self, 'registration_data', None)

    def registration_str(self):
        reg_data = self.try_get_registration_data()
        if not reg_data:
            return ""
        if not reg_data.registration_date:
            return reg_data.address
        return f"{reg_data.registration_date}, {reg_data.address}"

    def is_personal_data_filled(self, is_passport_required):
        is_ok = self.surname and self.date_birth is not None
        if is_passport_required:
            is_ok = is_ok and self.try_get_passport() is not None
        return is_ok

    def is_phone_filled(self):
        return self.first_phone_number_str() != ''

    def get_trip_company(self, trip):
        from main.models.trips.tourists.trip_company import TripCompany
        companies = getattr(self, 'trip_companies', TripCompany.objects.none())
        return companies.filter(trip=trip).first()

    def is_customer(self, trip):
        company = self.get_trip_company(trip)
        return company and company.get_customer() == self

    def get_roommates_group(self, trip_hotel_visit):
        return self.roommate_groups.filter(trip_hotel_visit=trip_hotel_visit).first()

    def get_roommates(self, trip_hotel_visit):
        # TODO: добавить тесты
        from main.models.clients.client import Client
        return Client.objects.exclude(pk=self.pk).filter(
            roommate_groups__trip_hotel_visit=trip_hotel_visit,
            roommate_groups__roommates=self,
        ).distinct()

    def arrival(self, trip):
        trip_and_client = self.tripandclient_set.filter(trip=trip).first()
        return trip_and_client.arrival() if trip_and_client else None

    def departure(self, trip):
        trip_and_client = self.tripandclient_set.filter(trip=trip).first()
        return trip_and_client.departure() if trip_and_client else None

    def arrival_and_departure_str(self, trip):
        arrival = self.arrival(trip)
        departure = self.departure(trip)
        if not arrival and not departure:
            return ''
        transfers = [arrival, departure]
        transfer_strings = [(x.short_date_time_str() if x else '-') for x in transfers]
        return ' / '.join(transfer_strings)

    def copy_transfer_from(self, other_transfer_pk):
        from main.models.trips.tourists.trip_airplane_transfer import TripAirplaneTransfer
        from main.models.trips.tourists.abstract_trip_transfer import AbstractTripTransfer

        other_transfer = TripAirplaneTransfer.objects.get(pk=other_transfer_pk)
        trip = other_transfer.trip_and_client.trip
        is_arrival = other_transfer.transfer_type == AbstractTripTransfer.TransferTypeEnum.ARRIVAL
        old_transfer = self.arrival(trip) if is_arrival else self.departure(trip)
        if old_transfer:
            old_transfer.delete()
        trip_and_client = self.tripandclient_set.filter(trip=trip).first()
        if not trip_and_client:
            return
        other_transfer.pk = None  # Способ получить копию модели - просто сбрасываем первичный ключ
        other_transfer.trip_and_client = trip_and_client
        other_transfer.save()

    def trips_sorted(self):
        trips_list = list(self.trips.filter(start_date__gte=date.today()).order_by('start_date'))
        trips_list += list(self.trips.filter(start_date__lt=date.today()).order_by('-start_date'))
        return trips_list

    def may_delete(self):
        return not self.trips.exists() and (not hasattr(self, 'owned_coupons') or not self.owned_coupons.exists())

    def as_payment_party(self, save=False):
        from main.models.money.person_payment_party import PersonPaymentParty
        current = PersonPaymentParty.objects.filter(person=self).first()
        if current:
            return current
        else:
            party = PersonPaymentParty(name=self.full_name(), person=self)
            if save:
                party.save()
            return party

    @staticmethod
    def annotate_full_name(query_set):
        return query_set.annotate(
            full_name_q=Trim(Concat('surname', models.Value(' '), 'name', models.Value(' '), 'middle_name')),
        )

    class Meta:
        abstract = True
