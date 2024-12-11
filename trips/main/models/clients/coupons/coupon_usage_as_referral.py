from django.db import models
from django.utils import timezone

from main.models.clients.coupons.coupon import Coupon
from main.models.clients.client import Client
from main.models.agency.agency_employee import AgencyEmployee


class CouponUsageAsReferral(models.Model):
    """Реализация купона в качестве реферальной ссылки."""
    coupon = models.ForeignKey(Coupon, on_delete=models.CASCADE, related_name='coupon_usages_as_referrals')
    used_by = models.OneToOneField(Client, on_delete=models.CASCADE, related_name='coupon_referral')

    created_by = models.ForeignKey(AgencyEmployee, on_delete=models.SET_NULL, blank=True, null=True,
                                   related_name='created_coupon_usages_as_referrals')
    created_at = models.DateTimeField('Дата создания', default=timezone.now, blank=True, null=True)

    def __str__(self):
        return f"{self.coupon}: реализован клиентом {self.used_by.full_name()}"

    class Meta:
        verbose_name = 'Купон - реализация в виде реферальной ссылки'
        verbose_name_plural = 'Купоны - реализации в виде реферальных ссылок'
