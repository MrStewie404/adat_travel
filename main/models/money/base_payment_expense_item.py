from django.db import models, transaction
from django.urls import reverse

from main.models.money.payment import Payment
from main.models.utils import create_price_field


class BasePaymentExpenseItem(models.Model):
    """
    Статья платежа - позволяет разбить платёж на несколько частей
    (базовый класс; производные классы привязывают платежи к договорам, услугам и т.д.).
    """
    payment = models.ForeignKey(Payment, on_delete=models.CASCADE, related_name='expense_items')
    amount = create_price_field('Сумма')

    def __str__(self):
        return f"{self.payment} / {self.amount}"

    @property
    def view_url(self):
        child = self.child_expense_item_or_self
        if child.url_name:
            return reverse(child.url_name, args=child.url_args)
        return ""

    @property
    def url_name(self):
        return None

    @property
    def url_args(self):
        return None

    @property
    def get_contract(self):
        return self.child_expense_item_or_self.get_contract_internal()

    def get_contract_internal(self):
        return None

    @property
    def short_text(self):
        return self.child_expense_item_or_self.short_text_internal()

    def short_text_internal(self):
        return self.__str__()

    @property
    def details_url(self):
        return self.child_expense_item_or_self.details_url_internal

    def details_url_internal(self):
        return ""

    @property
    def child_expense_item_or_self(self):
        child_fields = ['contract_expense_item', 'contract_service_expense_item', 'hotel_expense_item',
                        'trip_service_expense_item', 'guide_extra_expense_item', 'supplier_commission_expense_item']
        child_item = None
        for x in child_fields:
            child_item = child_item or getattr(self, x, None)
        return child_item or self

    def update_guide_payment_amount(self, amount, guide):
        with transaction.atomic():
            payment = self.payment
            payment.payer = guide.as_payment_party(save=True)
            payment.amount = amount
            payment.save()
            self.amount = amount
            self.save()

    class Meta:
        verbose_name = 'Статья платежа'
        verbose_name_plural = 'Статьи платежей'
