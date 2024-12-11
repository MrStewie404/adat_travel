from math import floor

from django.db import models

from main.models.abc_model import ABCModel
from main.models.agency.agency import Agency
from main.models.utils import create_price_field
from main.utils.utils import format_money


class CommissionTypeEnum(models.IntegerChoices):
    FIXED = 1, 'Фиксированная (в рублях)'
    PERCENT = 2, 'В % от суммы договора'

    __empty__ = '(Выберите вид комиссии)'


class SupplierManager(models.Manager):
    def get_by_natural_key(self, name, agency__name):
        return self.get(name=name, agency=Agency.objects.get_by_natural_key(agency__name) if agency__name else None)


class Supplier(ABCModel):
    """Контрагент."""

    class SupplierTypeEnum(models.IntegerChoices):
        PERSON = 1, 'Физическое лицо'
        LEGAL = 2, 'Юридическое лицо'

        __empty__ = '(Выберите тип контрагента)'

    agency = models.ForeignKey(Agency, on_delete=models.CASCADE, related_name='service_suppliers',
                               blank=True, null=True)
    name = models.CharField('Наименование', max_length=256)
    full_name = models.CharField('Полное наименование', max_length=256, blank=True)
    default_commission = create_price_field('Комиссия по умолчанию', default=0)
    default_commission_type = models.PositiveSmallIntegerField(
        'Вид комиссии по умолчанию',
        choices=CommissionTypeEnum.choices,
        default=CommissionTypeEnum.PERCENT,
    )

    objects = SupplierManager()

    def natural_key(self):
        agency_key = self.agency.natural_key() if self.agency else (None,)
        return (self.name,) + agency_key

    natural_key.dependencies = ['main.agency']

    @property
    def child_supplier(self):
        if hasattr(self, 'person_supplier'):
            return self.person_supplier
        return self.legal_supplier

    @property
    def supplier_type(self):
        return self.child_supplier.supplier_type

    @property
    def full_or_short_name(self):
        return self.full_name or self.name

    def __str__(self):
        return self.name or 'Аноним'

    def try_get_cabinet(self):
        return getattr(self, 'supplier_cabinet', None)

    def may_have_cabinet(self):
        # Если контрагент не привязан к агентству, то неизвестно, какие туры можно показывать в кабинете
        return self.agency is not None and self.agency.is_supplier_cabinet_enabled

    def may_delete(self):
        for service in self.services.all():
            if not service.may_delete():
                return False
        return True

    @property
    def any_name(self):
        return self.full_name or self.name

    def as_payment_party(self, save=False):
        from main.models.money.supplier_payment_party import SupplierPaymentParty
        current = SupplierPaymentParty.objects.filter(supplier=self).first()
        if current:
            return current
        else:
            party = SupplierPaymentParty(name=self.any_name, supplier=self)
            if save:
                party.save()
            return party

    def calc_default_commission(self, contract_price):
        return self.calc_commission(contract_price, self.default_commission, self.default_commission_type)

    def default_commission_str(self):
        if self.default_commission_type == CommissionTypeEnum.FIXED:
            return format_money(self.default_commission)
        return f"{int(self.default_commission)} %"

    @staticmethod
    def calc_commission(contract_price, commission_amount, commission_type):
        if commission_type == CommissionTypeEnum.FIXED:
            commission = commission_amount
        else:
            commission = commission_amount * contract_price / 100
        return floor(commission)

    class Meta:
        verbose_name = 'Контрагент'
        verbose_name_plural = 'Контрагенты'
        permissions = [
            ('manage_suppliers', 'Пользователь может управлять контрагентами, но не удалять их (#наше)'),
            ('manage_supplier_accounts', 'Пользователь может управлять аккаунтами контрагентов (личными кабинетами) (#наше)'),
            ('delete_suppliers', 'Пользователь может удалять контрагентов (#наше)'),
        ]
