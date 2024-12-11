import re

from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import UniqueConstraint, Q

from main.models.agency.agency import Agency


class ServiceLabelManager(models.Manager):
    def get_by_natural_key(self, name, agency__name):
        return self.get(name=name, agency=Agency.objects.get_by_natural_key(agency__name) if agency__name else None)


class ServiceLabel(models.Model):
    """Тип услуги (уникальная метка/тег)."""

    class PredefinedLabelEnum(models.TextChoices):
        """Предустановленные типы услуг."""
        EXCURSION = 'EXCURSION', 'Экскурсия'
        MEAL = 'MEAL', 'Питание'
        ACCOMMODATION = 'ACCOMMODATION', 'Размещение'
        GUIDE = 'GUIDE', 'Гид'
        TRANSPORT = 'TRANSPORT', 'Транспорт'

    default_color = '#F57C00'  # Оранжевый цвет по умолчанию

    agency = models.ForeignKey(Agency, on_delete=models.CASCADE, related_name='service_labels', blank=True, null=True)
    name = models.CharField('Имя', max_length=32)
    description = models.TextField('Описание', blank=True)
    color = models.CharField('Цвет', max_length=32, default=default_color)

    objects = ServiceLabelManager()

    def natural_key(self):
        agency_key = self.agency.natural_key() if self.agency else (None,)
        return (self.name,) + agency_key

    natural_key.dependencies = ['main.agency']

    def __str__(self):
        return self.name

    def is_predefined(self):
        return self.name in self.PredefinedLabelEnum.labels

    def validate_unique(self, exclude=None):
        super().validate_unique(exclude=exclude)
        agency = self.agency
        agency_filter = (Q(agency=None) | Q(agency=agency)) if agency else Q()
        if ServiceLabel.objects.exclude(pk=self.pk).filter(agency_filter, name=self.name).exists():
            raise ValidationError("Метка с таким названием уже существует.", code='name_not_unique')

    def clean_color(self):
        color = self.color
        if not re.match(r"^#[0-9a-fA-F]{6}$", color):
            raise ValidationError("Такой формат цвета не поддерживается.", code='color_check_fail')
        return color

    def save(self, *args, **kwargs):
        # Если мы создаём модель в коде, то при сохранении стоит для надёжности вызвать full_clean.
        self.full_clean()
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = 'Тип услуги'
        verbose_name_plural = 'Типы услуг'
        ordering = ('name',)
        constraints = [
            UniqueConstraint(fields=['agency', 'name'], name='%(app_label)s_%(class)s_is_unique'),
        ]
