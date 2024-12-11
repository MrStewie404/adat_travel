from django.db import models

from main.models.directory.city import City


class AbstractTripAndCity(models.Model):
    """Абстрактная модель: город ночёвки/посещения (для тура или для маршрута)."""

    class ObjectiveEnum(models.IntegerChoices):
        SIGHTSEEING = 1, 'Осмотр достопримечательностей'
        OVERNIGHT = 2, 'Ночёвка'

        __empty__ = '(Выберите цель посещения)'

    city = models.ForeignKey(City, on_delete=models.CASCADE)
    day = models.PositiveSmallIntegerField('День тура')
    objective = models.SmallIntegerField(
        'Цель посещения',
        choices=ObjectiveEnum.choices,
        default=ObjectiveEnum.OVERNIGHT,
    )

    class Meta:
        abstract = True
