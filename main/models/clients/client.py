from datetime import date

from django.db import models
from django.db.models.signals import post_delete
from django.dispatch import receiver

from main.models.agency.agency_employee import AgencyEmployee
from main.models.clients.coupons.coupon_label import CouponLabel
from main.models.clients.person import Person
from main.models.services.supplier import Supplier


class Client(Person):
    """Клиент турфирмы."""
    person = models.OneToOneField(Person, on_delete=models.CASCADE, parent_link=True, related_name='client')
    responsible_person = models.ForeignKey(AgencyEmployee, on_delete=models.SET_NULL, blank=True, null=True,
                                           related_name='clients')
    supplier = models.ForeignKey(Supplier, on_delete=models.SET_NULL, blank=True, null=True, related_name='clients')
    is_created_by_external_user = models.BooleanField('Самозапись', default=False)

    def try_get_inbox_client_data(self, inbox_trip_company):
        return self.inbox_client_data_set.filter(inbox_trip_company=inbox_trip_company).first()

    def owned_certificates(self):
        return self.owned_coupons.filter(label__label_type=CouponLabel.LabelTypeEnum.CERTIFICATE)

    def owned_promo_code(self):
        return self.owned_coupons.filter(label__label_type=CouponLabel.LabelTypeEnum.PROMO_CODE).first()

    def try_get_coupon_referral_usage(self):
        return getattr(self, 'coupon_referral', None)

    @property
    def email(self):
        if self.emails.count() > 0:
            return self.emails.all()[0].email

        return ""


    def get_valid_referral_coupon_for(self, trip):
        coupon_referral_usage = self.try_get_coupon_referral_usage()
        coupon_referral = coupon_referral_usage.coupon if coupon_referral_usage else None
        if not coupon_referral or not coupon_referral.is_active:
            return None
        # Если клиент не новый и уже побывал в каком-нибудь туре (кроме указанного), то возвращаем None
        if not self.is_new_customer(exclude_trip=trip):
            return None
        # Если клиент ранее пользовался каким-либо промокодом, то возвращаем None
        from main.models.clients.coupons.coupon_usage_in_trip import CouponUsageInTrip
        if CouponUsageInTrip.objects.\
                filter(coupon__label=CouponLabel.default_promo_code_label(self.agency),
                       contract__customer=self).\
                exclude(contract__trip_company__trip=trip).exists():
            return None
        return coupon_referral

    def is_new_customer(self, exclude_trip):
        return not self.trips.exclude(pk=exclude_trip.pk).filter(start_date__lt=date.today()).exists()

    class Meta:
        verbose_name = 'Клиент'
        verbose_name_plural = 'Клиенты'
        permissions = [
            ('manage_clients', 'Пользователь может управлять персональными данными гостей, но не удалять их (#наше)'),
            ('delete_clients', 'Пользователь может удалять гостей (#наше)'),
            ('export_clients', 'Пользователь может экспортировать персональные данные гостей (#наше)'),
        ]


@receiver(post_delete, sender='main.Client')
def post_delete_client(sender, instance, **kwargs):
    from main.models.trips.tourists.trip_company import TripCompany
    from main.models.trips.accommodation.abstract_trip_roommates_group import AbstractTripRoommatesGroup
    for company in instance.trip_companies.all():
        TripCompany.remove_from_company(instance, company)
    for group in instance.roommate_groups.all():
        AbstractTripRoommatesGroup.remove_from_roommates_group(instance, group)
