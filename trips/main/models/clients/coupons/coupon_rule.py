from django.db import models

from main.models.clients.coupons.coupon import Coupon


class CouponRule(models.Model):
    """Правило использования купона."""
    coupon = models.ForeignKey(Coupon, on_delete=models.CASCADE, related_name='rules')

    def __str__(self):
        return f"{self.coupon}: правило"

    class Meta:
        verbose_name = 'Правило купона'
        verbose_name_plural = 'Правила купонов'
