import re

from django.db import models
from django.db.models import UniqueConstraint
from main.utils.home_folder import HomeFolder


class AgencyManager(models.Manager):
    def get_by_natural_key(self, name):
        return self.get(name=name)


class Agency(models.Model):
    name = models.CharField('Название', max_length=64)
    phone_number = models.CharField('Телефон', max_length=32, blank=True)
    email = models.EmailField('E-Mail', blank=True)
    website = models.URLField('Web-сайт', blank=True)
    legal_address = models.CharField('Юридический адрес', max_length=512, blank=True)
    actual_address = models.CharField('Фактический адрес', max_length=512, blank=True)
    requisites = models.TextField('Реквизиты', blank=True)
    is_supplier_cabinet_enabled = models.BooleanField('Включить кабинет контрагента (и самозапись)', default=False)
    is_trip_auto_update_schedule_enabled = models.BooleanField(
        'Показывать галочку для автоматического обновления услуг и дней из шаблона',
        default=False,
    )
    yandex_metrics_id = models.CharField('ID счётчика в Яндекс Метрике', max_length=32, blank=True)
    max_days_to_edit_finished_trips = models.PositiveSmallIntegerField(
        'Сколько дней после окончания тура разрешается его редактировать',
        default=3,
    )
    days_before_trip_to_show_details_for_guide = models.PositiveSmallIntegerField(
        'За сколько дней до начала тура гид видит список группы и другие детали',
        default=3,
    )
    days_after_trip_to_show_details_for_guide = models.PositiveSmallIntegerField(
        'Сколько дней после окончания тура гид видит список группы и другие детали',
        default=2,
    )

    objects = AgencyManager()

    def natural_key(self):
        return (self.name,)

    def __str__(self):
        return self.name

    @property
    def phone_number_formatted(self):
        from main.templatetags import format_extensions
        return format_extensions.phonenumber(self.phone_number)

    def get_whatsapp_number_for_url(self):
        from main.models.clients.abstract_social_network_contact import AbstractSocialNetworkContact
        contact = self.social_network_contacts.filter(
            social_network=AbstractSocialNetworkContact.SocialNetworkTypeEnum.WHATSAPP,
        ).first()
        if not contact:
            return None
        return re.sub(r'\D', '', contact.account)  # убираем все нецифровые символы

    def try_get_payment_token(self):
        return getattr(self, 'payment_token', None)

    def as_payment_party(self, save=False):
        from main.models.money.agency_payment_party import AgencyPaymentParty
        current = AgencyPaymentParty.objects.filter(agency=self).first()
        if current:
            return current
        else:
            party = AgencyPaymentParty(name=self.name, agency=self)
            if save:
                party.save()
            return party

    @property
    def home_folder(self):
        return HomeFolder.for_agency(self)

    @property
    def logo_path(self):
        return self.home_folder.file_path_logo

    @property
    def favicon_path(self):
        return self.home_folder.file_path_favicon

    @property
    def report_logo_path(self):
        return self.home_folder.file_path_report_logo

    @property
    def supplier_cabinet_logo_path(self):
        return self.home_folder.file_path_supplier_cabinet_logo

    @property
    def supplier_cabinet_navbar_theme_light_path(self):
        return self.home_folder.file_path_supplier_cabinet_navbar_theme_light

    @property
    def reports_path(self):
        return self.home_folder.path_reports

    @property
    def contracts_path(self):
        return self.home_folder.path_contracts

    @property
    def mails_path(self):
        return self.home_folder.path_mails

    @staticmethod
    def get_valid_filename(agency, prepend_pk):
        from main.utils.utils import get_transliterated_filename
        if agency:
            name = agency.name.lower()[:16]
            if prepend_pk:
                name = f"{agency.pk}_{name}"
        else:
            name = '__common__'
        name = get_transliterated_filename(name)
        return name

    class Meta:
        verbose_name = 'Агентство'
        verbose_name_plural = 'Агентства'
        constraints = [
            UniqueConstraint(fields=['name'], name='%(app_label)s_%(class)s_name_is_unique'),
        ]
