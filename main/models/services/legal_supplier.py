from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q

from main.models.services.supplier import Supplier


class LegalSupplier(Supplier):
    """Контрагент - юридическое лицо."""
    supplier = models.OneToOneField(Supplier, on_delete=models.CASCADE, parent_link=True,
                                    related_name='legal_supplier')
    address = models.CharField('Юридический адрес', max_length=256, blank=True)
    phone_number = models.CharField('Телефон', max_length=32, blank=True)
    email = models.EmailField('E-mail', blank=True)
    website = models.URLField('Официальный сайт', blank=True)
    lat = models.FloatField('Широта', blank=True, null=True)
    lon = models.FloatField('Долгота', blank=True, null=True)
    inn = models.CharField('ИНН', max_length=12, blank=True)
    kpp = models.CharField('КПП', max_length=9, blank=True)
    bank_details = models.TextField('Банковские реквизиты', blank=True)
    comment = models.TextField('Комментарий', blank=True)

    @property
    def supplier_type(self):
        return Supplier.SupplierTypeEnum.LEGAL

    def get_duplicate_supplier(self):
        agency = self.agency
        agency_filter = (Q(agency=None) | Q(agency=agency)) if agency else Q()
        return Supplier.objects.exclude(pk=self.pk).filter(agency_filter, name=self.name).first()

    def validate_unique(self, exclude=None):
        super().validate_unique(exclude=exclude)
        duplicate_supplier = self.get_duplicate_supplier()
        if duplicate_supplier:
            raise ValidationError("Контрагент с таким именем уже существует.", code='supplier_not_unique',
                                  params=[duplicate_supplier])

    class Meta:
        verbose_name = 'Контрагент - юридическое лицо'
        verbose_name_plural = 'Контрагенты - юридические лица'
