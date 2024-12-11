from django.db import models
from django.db.models import UniqueConstraint

from main.models.custom_unique_error_mixin import CustomUniqueErrorMixin
from main.models.hotels.hotel import Hotel
from main.models.utils import create_price_field


class HotelRoomTypeManager(models.Manager):
    def get_by_natural_key(self, name, *hotel_args):
        return self.get(name=name, hotel=Hotel.objects.get_by_natural_key(*hotel_args))


class HotelRoomType(CustomUniqueErrorMixin, models.Model):
    """Тип комнаты в отеле (привязан к конкретному отелю, т.к. у каждого отеля могут быть свои особенности)."""

    class RoomTypeEnum(models.TextChoices):
        SINGLE = 'SINGLE', '1-местный (с маленькой кроватью)'
        SINGLE_BIG_BED = 'SINGLE_BIG_BED', '1-местный с большой кроватью'
        DOUBLE_TWIN_BEDS = 'DOUBLE_TWIN_BEDS', '2-местный с раздельными кроватями'
        DOUBLE_BIG_BED = 'DOUBLE_BIG_BED', '2-местный с большой кроватью'
        DOUBLE_UNIVERSAL = 'DOUBLE_UNIVERSAL', '2-местный универсальный'
        TRIPLE_THREE_BEDS = 'TRIPLE_THREE_BEDS', '3-местный с раздельными кроватями'
        TRIPLE_BIG_BED = 'TRIPLE_BIG_BED', '3-местный с большой кроватью'
        TRIPLE_UNIVERSAL = 'TRIPLE_UNIVERSAL', '3-местный универсальный'
        QUAD = 'QUAD', '4-местный'

        __empty__ = '(Выберите категорию номера)'

    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE, related_name='room_types')
    name = models.CharField('Название номера', max_length=256)
    room_type = models.CharField(
        'Категория номера',
        max_length=32,
        choices=RoomTypeEnum.choices,
        blank=False,
    )
    total_area = models.FloatField('Площадь', blank=True, null=True)
    rooms_count = models.PositiveSmallIntegerField('Число комнат', default=1)
    min_adults_count = models.PositiveSmallIntegerField('Минимальное число взрослых гостей', default=1)
    max_adults_count = models.PositiveSmallIntegerField('Максимальное число взрослых гостей')
    max_children_count = models.PositiveSmallIntegerField('Максимальное число детей', blank=True, null=True)
    price = create_price_field('Цена', blank=True, null=True)
    price_single = create_price_field('Цена за одноместное размещение', blank=True, null=True)
    comment = models.TextField('Другие особенности номера', blank=True)

    objects = HotelRoomTypeManager()

    def natural_key(self):
        return (self.name,) + self.hotel.natural_key()

    natural_key.dependencies = ['main.hotel']

    def __str__(self):
        return self.name

    def may_delete(self):
        return not self.pre_bookings.exists()

    def get_unique_together_error_message(self):
        return "Номер с таким названием уже есть в гостинице. Пожалуйста, измените название номера."

    class Meta:
        verbose_name = 'Тип номера'
        verbose_name_plural = 'Типы номеров'
        constraints = [
            UniqueConstraint(fields=['hotel', 'name'], name='%(app_label)s_%(class)s_name_is_unique'),
        ]
