from django.db import models
from django.db.models import UniqueConstraint

from main.models.abstract_media import AbstractMedia
from main.models.money.payment import Payment


class PaymentMedia(AbstractMedia):
    """Файл, прикреплённый к платежу пользователем."""
    payment = models.ForeignKey(Payment, on_delete=models.CASCADE, related_name='payment_media_files')

    def __str__(self):
        return f"{self.payment}, {self.file.name}, {self.description}"

    @property
    def agency(self):
        return self.payment.agency

    @classmethod
    def create_check(cls, payment, file):
        return PaymentMedia.objects.create(payment=payment, file=file, description="Чек по операции")

    class Meta:
        verbose_name = 'Медиафайл к платежу'
        verbose_name_plural = 'Медиафайлы к платежам'
        constraints = [
            UniqueConstraint(fields=['payment', 'file'], name='%(app_label)s_%(class)s_is_unique'),
        ]
