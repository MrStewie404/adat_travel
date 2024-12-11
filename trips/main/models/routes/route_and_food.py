from django.db import models
from django.db.models import UniqueConstraint

from main.models.routes.route import Route


class RouteAndFoodManager(models.Manager):
    def get_by_natural_key(self, day, *route_args):
        return self.get(day=day, route=Route.objects.get_by_natural_key(*route_args))


class RouteAndFood(models.Model):
    """Питание на маршруте."""

    class MealTypeEnum(models.TextChoices):
        NO = 'NO', 'Без питания'
        BB = 'BB', 'Завтрак'
        HB = 'HB', 'Завтрак+ужин'
        FB = 'FB', 'Полный пансион'

        __empty__ = '(Выберите тип питания)'

    route = models.ForeignKey(Route, on_delete=models.CASCADE)
    day = models.PositiveSmallIntegerField('День тура')
    meal_type = models.CharField(
        'Питание',
        max_length=2,
        choices=MealTypeEnum.choices,
        blank=False,
    )
    comment = models.TextField('Комментарий', blank=True)

    objects = RouteAndFoodManager()

    def natural_key(self):
        return (self.day,) + self.route.natural_key()

    natural_key.dependencies = ['main.route']

    def __str__(self):
        return f"{self.route}, {self.day}, {self.meal_type}"

    class Meta:
        verbose_name = 'Маршрут - питание'
        verbose_name_plural = 'Маршруты - питание'
        constraints = [
            UniqueConstraint(fields=['route', 'day'], name='%(app_label)s_%(class)s_is_unique'),
        ]
