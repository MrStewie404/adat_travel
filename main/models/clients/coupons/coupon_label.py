from django.db import models
from django.db.models import UniqueConstraint

from main.models.agency.agency import Agency


class CouponLabelManager(models.Manager):
    def get_by_natural_key(self, name, agency__name):
        return self.get(name=name, agency=Agency.objects.get_by_natural_key(agency__name))


class CouponLabel(models.Model):
    """
    Тип купона (уникальная метка/тег).
    Имеется ограниченный набор предустановленных типов (сертификат, промокод и т.д.), различаемых системой.
    Для каждого из этих типов можно создавать несколько пользовательских (под)типов с разными именами.
    """

    class LabelTypeEnum(models.TextChoices):
        CERTIFICATE = 'CERTIFICATE', 'Сертификат'
        PROMO_CODE = 'PROMO_CODE', 'Промокод'
        OTHER = 'OTHER', 'Другое'

        __empty__ = '(Выберите тип купона)'

    agency = models.ForeignKey(Agency, on_delete=models.CASCADE, related_name='coupon_labels')
    name = models.CharField('Наименование', max_length=32)
    label_type = models.CharField(
        'Тип купона',
        max_length=16,
        choices=LabelTypeEnum.choices,
        blank=False,
    )
    description = models.TextField('Описание', blank=True)

    objects = CouponLabelManager()

    def natural_key(self):
        return (self.name,) + self.agency.natural_key()

    natural_key.dependencies = ['main.agency']

    def __str__(self):
        return self.name

    @staticmethod
    def default_promo_code_label(agency):
        # Пока что для простоты считаем, что у нас в БД может быть только одна метка для промокодов и для сертификатов.
        (label, _) = CouponLabel.objects.get_or_create(
            agency=agency,
            label_type=CouponLabel.LabelTypeEnum.PROMO_CODE,
            defaults={'name': 'Промокод'},
        )
        return label

    @staticmethod
    def default_certificate_label(agency):
        (label, _) = CouponLabel.objects.get_or_create(
            agency=agency,
            label_type=CouponLabel.LabelTypeEnum.CERTIFICATE,
            defaults={'name': 'Подарочный сертификат'},
        )
        return label

    class Meta:
        verbose_name = 'Тип купона'
        verbose_name_plural = 'Типы купонов'
        constraints = [
            UniqueConstraint(fields=['agency', 'name'], name='%(app_label)s_%(class)s_is_unique'),
        ]
