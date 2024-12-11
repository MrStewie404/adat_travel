import logging
from datetime import date

from django.core.exceptions import ValidationError
from django.db import transaction
from django.forms import IntegerField, DecimalField, BooleanField, CharField, DateField, TypedChoiceField, EmailField, \
    ModelChoiceField

from main.forms.clients.base_person_form import BasePersonForm
from main.forms.common.widgets import money_input, checkbox, number_input, text_input, date_input, select, email_input, \
    rich_select
from main.models.clients.abstract_email_contact import AbstractEmailContact
from main.models.clients.abstract_phone_contact import AbstractPhoneContact
from main.models.clients.client import Client
from main.models.clients.person_email_contact import PersonEmailContact
from main.models.clients.person_phone_contact import PersonPhoneContact
from main.models.services.supplier import CommissionTypeEnum
from main.models.trips.departure_point import DeparturePoint
from main.models.trips.tourists.trip_company import TripCompany
from main.models.utils import price_max_digits, price_decimal_places
from main.validators.phone_validator import clean_and_validate_phone


class BaseAddTouristForm(BasePersonForm):
    true_false_choices = ((True, 'Да'), (False, 'Нет'))

    phone_number = CharField(widget=text_input(''), label='Телефон', required=True)
    email = EmailField(widget=email_input(), label='E-Mail (для информации о туре)', required=False)
    tourists_count = IntegerField(
        min_value=1,
        widget=number_input(''),
        label='Количество гостей',
        required=True,
        initial=1,
    )
    trip_date = DateField(
        widget=date_input(css_class='form-control'),
        label='Дата тура',
    )
    departure_point = ModelChoiceField(
        queryset=DeparturePoint.objects.none(),
        widget=rich_select('', css_class=''),
        label='Место сбора',
        empty_label='(Выберите место сбора)',
        required=False,
    )
    supplier_commission = DecimalField(
        max_digits=price_max_digits,
        decimal_places=price_decimal_places,
        widget=money_input(''),
        label='Размер комиссии, ₽',
        min_value=0,
        disabled=True,
    )
    is_commission_paid = TypedChoiceField(
        coerce=lambda x: x == 'True',
        choices=true_false_choices,
        widget=select(width="100%", height=35),
        label='Комиссия оплачена',
        initial=False,
        required=False,
    )
    has_children_pre7 = TypedChoiceField(
        coerce=lambda x: x == 'True',
        choices=true_false_choices,
        widget=select(width="100%", height=35),
        label='Будут ли с вами дети до 7 лет?',
        initial=False,
        required=True,
    )
    agree_with_policies = BooleanField(
        widget=checkbox(css_class='custom-checkbox-crispy'),
        label='',
        initial=False,
        required=True,
    )

    def __init__(self, *args, **kwargs):
        self.agency = kwargs.pop('agency')
        self.trips_queryset = kwargs.pop('trips_queryset')
        super().__init__(*args, **kwargs)
        departure_points = self.agency.departure_points.filter(trips__in=self.trips_queryset).distinct()
        if departure_points:
            self.fields['departure_point'].queryset = departure_points
            # if departure_points.count() == 1:
                # self.initial['departure_point'] = departure_points.first().pk
                # self.fields['departure_point'].disabled = True
        else:
            self.fields.pop('departure_point')

    def get_cleaned_trip(self):
        trip_date = self.cleaned_data.get('trip_date')
        return self.trips_queryset.filter(start_date=trip_date).first()

    def clean_phone_number(self):
        return clean_and_validate_phone(self.cleaned_data['phone_number'])

    def clean_trip_date(self):
        trip_date = self.cleaned_data.get('trip_date')
        if trip_date <= date.today():
            raise ValidationError("Дата тура должна быть в будущем", code='trip_date_check_fail')
        return trip_date

    def clean_agree_with_policies(self):
        agree = self.cleaned_data.get('agree_with_policies')
        if not agree:
            raise ValidationError("Для продолжения необходимо подтвердить согласие с условиями предоставления услуги",
                                  code='agree_check_fail')
        return agree

    def clean(self):
        cleaned_data = super().clean()
        commission = cleaned_data.get('supplier_commission')
        is_commission_paid = cleaned_data.get('is_commission_paid')
        tourists_count = cleaned_data.get('tourists_count')
        phone_number = self.cleaned_data.get('phone_number')
        departure_point = self.cleaned_data.get('departure_point')
        trip = self.get_cleaned_trip()

        if not trip:
            raise ValidationError("Не найдены туры на выбранную дату", code='trip_not_found')

        if tourists_count and tourists_count > trip.free_seats_count():
            raise ValidationError("Недостаточно мест в туре", code='not_enough_free_seats')

        if commission and tourists_count:
            max_commission = trip.price * tourists_count
            if commission > max_commission:
                raise ValidationError("Комиссия не должна превышать стоимость тура", code='commission_too_big')

        if is_commission_paid and not commission:
            raise ValidationError("Не указан размер оплаченной комиссии", code='commission_paid_but_zero')

        if trip.departure_points.exists() and not departure_point:
            raise ValidationError("Необходимо выбрать место сбора", code='departure_point_null')

        if departure_point and departure_point not in trip.departure_points.all():
            raise ValidationError("К сожалению, выбранное место сбора не предусмотрено для этого тура",
                                  code='bad_departure_point')

        if phone_number:
            existing_clients = Client.objects.filter(trips__pk=trip.pk, phone_numbers__phone_number=phone_number).\
                distinct()
            if existing_clients.count() >= 5:
                msg = "Превышен лимит заявок для гостя"
                logging.warning(f"{msg} {self._get_tourist_info_str()}")
                raise ValidationError(msg, code='duplicate_clients_limit_reached')
            existing_companies = TripCompany.objects.filter(
                trip__agency=trip.agency,
                tourists__phone_numbers__phone_number=phone_number,
            ).distinct()
            if existing_companies.count() >= 50:
                msg = "Превышен лимит туров для гостя"
                logging.warning(f"{msg} {self._get_tourist_info_str()}")
                raise ValidationError(msg, code='trips_limit_reached')
        return cleaned_data

    def save_as_new_or_existing_tourist(self, supplier):
        tourists_count = self.cleaned_data.get('tourists_count', 1)
        phone_number = self.cleaned_data.get('phone_number')
        email = self.cleaned_data.get('email')
        departure_point = self.cleaned_data.get('departure_point')
        trip = self.get_cleaned_trip()
        default_commission = supplier.calc_default_commission(trip.price * tourists_count)
        supplier_commission = default_commission
        commission_type = CommissionTypeEnum.FIXED
        is_commission_paid = self.cleaned_data.get('is_commission_paid', False)
        has_children_pre7 = self.cleaned_data.get('has_children_pre7', False)
        instance = self.instance
        instance.agency = trip.agency
        instance.supplier = supplier
        instance.is_created_by_external_user = True
        existing_tourist = Client.objects.filter(
            agency=instance.agency,
            supplier=instance.supplier,
            name=instance.name,
            surname=instance.surname,
            middle_name=instance.middle_name,
            phone_numbers__phone_number=phone_number,
        ).exclude(trips__pk=trip.pk).first()

        with transaction.atomic():
            if not existing_tourist:
                tourist = self.save()
                PersonPhoneContact.objects.create(
                    person=tourist,
                    phone_number=phone_number,
                    phone_type=AbstractPhoneContact.default_phone_type,
                )
            else:
                tourist = existing_tourist

            if email:
                PersonEmailContact.objects.get_or_create(
                    person=tourist,
                    email=email,
                    email_type=AbstractEmailContact.default_email_type,
                )

            company = trip.add_tourist(tourist)
            company.expected_tourists_count = tourists_count
            company.supplier = supplier
            company.supplier_commission = supplier_commission
            company.commission_type = commission_type
            company.is_created_by_external_user = True
            company.is_draft = True
            company.has_children_pre7 = has_children_pre7
            company.departure_point = departure_point
            company.save()
            default_prepayment = trip.default_prepayment * tourists_count
            contract = company.create_default_partially_filled_contract(postfix="_auto")
            contract.customer = tourist
            contract.prepayment = supplier_commission if is_commission_paid else default_prepayment
            contract.save()
            if is_commission_paid:
                company.add_commission_payment(
                    owner=None,
                    payment_amount=supplier_commission,
                    payment_date=date.today(),
                    payer=trip.agency.as_payment_party(save=True),
                    account=None,
                )
                contract.add_payment(
                    owner=None,
                    payment_amount=supplier_commission,
                    contract_part_amount=supplier_commission,
                    is_prepayment=True,
                    payment_date=date.today(),
                    account=None,
                )

        return tourist, company

    def _get_tourist_info_str(self):
        name = self.cleaned_data.get('name')
        surname = self.cleaned_data.get('surname')
        phone_number = self.cleaned_data.get('phone_number')
        return f"{name} {surname} / {phone_number}"

    class Meta(BasePersonForm.Meta):
        model = Client
        fields = ['surname', 'name', 'middle_name', 'phone_number', 'tourists_count', 'trip_date',
                  'supplier_commission', 'is_commission_paid', 'has_children_pre7', 'agree_with_policies']
