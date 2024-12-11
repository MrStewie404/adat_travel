from django.db import models

from main.models.clients.coupons.coupon_rule import CouponRule


class CouponExpirationRule(CouponRule):
    """Срок действия купона (до указанной даты включительно)."""
    coupon_rule_ptr = models.OneToOneField(CouponRule, on_delete=models.CASCADE, parent_link=True,
                                           related_name='expiration_rule')
    expires_after = models.DateField('Действителен до даты')

    def __str__(self):
        return f"{self.coupon}: срок действия"

    class Meta:
        verbose_name = 'Правило купона - срок действия'
        verbose_name_plural = 'Правила купонов - сроки действия'
