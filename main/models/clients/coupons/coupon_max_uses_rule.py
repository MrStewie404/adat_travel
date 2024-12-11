from django.db import models

from main.models.clients.coupons.coupon_rule import CouponRule


class CouponMaxUsesRule(CouponRule):
    """Максимальное число использований купона."""
    coupon_rule_ptr = models.OneToOneField(CouponRule, on_delete=models.CASCADE, parent_link=True,
                                           related_name='max_uses_rule')
    max_uses_total = models.PositiveSmallIntegerField('Макс. общее число использований', blank=True, null=True)
    max_uses_per_user = models.PositiveSmallIntegerField('Макс. число использований каждым гостем',
                                                         blank=True, null=True)

    def __str__(self):
        return f"{self.coupon}: макс. использ."

    class Meta:
        verbose_name = 'Правило купона - число использований'
        verbose_name_plural = 'Правила купонов - число использований'
