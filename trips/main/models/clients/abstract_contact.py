from django.db import models


class AbstractContact(models.Model):
    """Абстрактная модель: контакт для связи."""

    class Meta:
        abstract = True
