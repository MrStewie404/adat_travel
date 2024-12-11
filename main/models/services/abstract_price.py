from django.db import models

from main.models.utils import create_price_field


class AbstractPrice(models.Model):
    """Абстрактная модель: стоимость услуги (или другого тур. продукта)."""

    class PriceTypeEnum(models.IntegerChoices):
        PER_PERSON = 1, 'За одного гостя'
        PER_GROUP = 2, 'За группу'

        __empty__ = '(Выберите категорию цены)'

    cost = create_price_field('Стоимость')
    price_type = models.SmallIntegerField(
        'Категория цены',
        choices=PriceTypeEnum.choices,
        default=PriceTypeEnum.PER_PERSON,
    )

    def get_price(self, person_count):
        result = self.cost
        if self.price_type == self.PriceTypeEnum.PER_PERSON:
            result = result * person_count
        return result

    class Meta:
        abstract = True
