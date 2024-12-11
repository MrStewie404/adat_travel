from django.db import models


class AbstractTripDay(models.Model):
    """Абстрактная модель: день тура или маршрута."""
    day = models.PositiveSmallIntegerField('День тура')
    caption = models.TextField('Краткое описание', max_length=256)

    class Meta:
        abstract = True
