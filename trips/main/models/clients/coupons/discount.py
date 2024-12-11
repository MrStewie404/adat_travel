from django.db import models

from main.models.agency.agency import Agency
from main.models.utils import create_price_field
from main.templatetags.format_extensions import currency
from main.templatetags.pluralize_ru import pluralize_ru


class Discount(models.Model):
    """Скидка."""

    class DiscountTypeEnum(models.TextChoices):
        FIXED_AMOUNT = 'FIXED_AMOUNT', 'Фиксированная (в рублях)'
        PERCENT = 'PERCENT', 'В % от стоимости тура'
        FREE_DAYS = 'FREE_DAYS', 'Дни в подарок'

        __empty__ = '(Выберите вид скидки)'

    agency = models.ForeignKey(Agency, on_delete=models.CASCADE, related_name='discounts')
    value = create_price_field('Величина скидки')
    discount_type = models.CharField(
        'Вид скидки',
        max_length=16,
        choices=DiscountTypeEnum.choices,
        blank=False,
    )

    def __str__(self):
        v = self.value_rounded
        if self.discount_type == self.DiscountTypeEnum.PERCENT:
            return f"{v}%"
        if self.discount_type == self.DiscountTypeEnum.FREE_DAYS:
            return f"{v} {pluralize_ru(v, 'день,дня,дней')}"
        return currency(v)

    @property
    def value_rounded(self):
        if self.discount_type in (self.DiscountTypeEnum.PERCENT, self.DiscountTypeEnum.FREE_DAYS):
            return round(self.value)
        return self.value

    class Meta:
        verbose_name = 'Скидка'
        verbose_name_plural = 'Скидки'
