from datetime import datetime
from decimal import Decimal

from django.db import models
from django.db.models import UniqueConstraint
from django.utils import timezone

from main.models.clients.coupons.coupon_label import CouponLabel
from main.models.clients.coupons.discount import Discount
from main.models.clients.client import Client
from main.models.agency.agency_employee import AgencyEmployee
from main.models.custom_unique_error_mixin import CustomUniqueErrorMixin
from main.models.utils import create_price_field


class Coupon(CustomUniqueErrorMixin, models.Model):
    """Купон (подарочный сертификат, промокод и т.п.)."""

    class StatusEnum(models.TextChoices):
        SOLD = 'SOLD', 'Продан/выдан'  # Или опубликован
        USED = 'USED', 'Реализован'    # Пока что актуален только для сертификатов

        __empty__ = '(Выберите статус)'

    label = models.ForeignKey(CouponLabel, on_delete=models.CASCADE, related_name='coupons')
    # Владелец (покупатель) сделан необязательным, т.к. могут быть анонимные купоны
    # Возможно, стоит явно выделить две дочерние модели: AnonymousCoupon и CouponWithOwner.
    owner = models.ForeignKey(Client, on_delete=models.SET_NULL, blank=True, null=True,
                              related_name='owned_coupons')
    # Может пригодиться на случай, если кто-то удалит покупателя
    owner_full_name = models.CharField('ФИО покупателя', max_length=128)
    number = models.CharField('Номер/код', max_length=16)
    issue_date = models.DateField('Дата продажи/публикации', default=timezone.now)
    price = create_price_field('Стоимость', default=0)
    discount = models.OneToOneField(Discount, on_delete=models.CASCADE, related_name='coupon')
    status = models.CharField(
        'Статус',
        max_length=16,
        choices=StatusEnum.choices,
        blank=False,
    )
    comment = models.TextField('Комментарий', blank=True)
    is_active = models.BooleanField('Действующий', default=True)

    created_by = models.ForeignKey(AgencyEmployee, on_delete=models.SET_NULL, blank=True, null=True,
                                   related_name='created_coupons')
    created_at = models.DateTimeField('Дата создания', default=timezone.now, blank=True, null=True)
    modified_by = models.ForeignKey(AgencyEmployee, on_delete=models.SET_NULL, blank=True, null=True,
                                    related_name='modified_coupons')
    modified_at = models.DateTimeField('Дата изменения', default=timezone.now, blank=True, null=True)

    @property
    def agency(self):
        return self.label.agency

    def __str__(self):
        return f"{self.label} {self.number}"

    def usages_in_started_trips_count(self):
        return self.coupon_usages_in_trips.filter(contract__trip_company__trip__start_date__lt=datetime.today()).count()

    def get_related_contracts_for(self, customer):
        return [x.contract for x in self.coupon_usages_in_trips.filter(contract__customer=customer)]

    def get_unique_together_error_message(self):
        return "Указанный номер (код) уже используется."

    @staticmethod
    def create_default_promo_code(client, created_by, code=None, save=True):
        if client.owned_promo_code():
            return None

        label = CouponLabel.default_promo_code_label(client.agency)
        discount = Discount(
            agency=client.agency,
            discount_type=Discount.DiscountTypeEnum.PERCENT,
            value=Decimal(5),
        )
        discount.save()

        from main.business_logic.promo_code_utils import default_code_for_client
        coupon = Coupon(
            label=label,
            number=code or default_code_for_client(client),
            owner=client,
            owner_full_name=client.full_name(),
            issue_date=timezone.now(),
            discount=discount,
            status=Coupon.StatusEnum.SOLD,
            created_by=created_by,
        )

        if save:
            coupon.save()
        return coupon

    class Meta:
        verbose_name = 'Купон'
        verbose_name_plural = 'Купоны'
        constraints = [
            UniqueConstraint(fields=['label', 'number'], name='%(app_label)s_%(class)s_is_unique'),
        ]
        permissions = [
            ('manage_coupons', 'Пользователь может управлять промокодами и сертификатами (#наше)'),
        ]
