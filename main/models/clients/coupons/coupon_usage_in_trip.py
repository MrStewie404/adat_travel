from django.db import models
from django.db.models import UniqueConstraint
from django.utils import timezone

from main.models.agency.agency_employee import AgencyEmployee
from main.models.clients.coupons.coupon import Coupon
from main.models.trips.tourists.client_contract.client_contract import ClientContract


class CouponUsageInTrip(models.Model):
    """Реализация купона в туре компанией туристов."""
    coupon = models.ForeignKey(Coupon, on_delete=models.CASCADE, related_name='coupon_usages_in_trips')
    contract = models.ForeignKey(ClientContract, on_delete=models.CASCADE, related_name='used_coupons')

    created_by = models.ForeignKey(AgencyEmployee, on_delete=models.SET_NULL, blank=True, null=True,
                                   related_name='created_coupon_usages_in_trips')
    created_at = models.DateTimeField('Дата создания', default=timezone.now, blank=True, null=True)

    def __str__(self):
        return f"{self.coupon}: реализован в туре {self.contract.trip_company.trip}"

    class Meta:
        verbose_name = 'Купон - реализация в туре'
        verbose_name_plural = 'Купоны - реализации в турах'
        constraints = [
            UniqueConstraint(fields=['coupon', 'contract'], name='%(app_label)s_%(class)s_is_unique'),
        ]
