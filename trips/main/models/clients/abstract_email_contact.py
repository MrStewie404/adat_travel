from django.db import models

from main.models.clients.abstract_contact import AbstractContact


class AbstractEmailContact(AbstractContact):
    """Абстрактная модель: e-mail для связи."""

    class EmailTypeEnum(models.TextChoices):
        WORK = 'WORK', 'Рабочий'
        PERSONAL = 'PERSONAL', 'Личный'
        OTHER = 'OTHER', 'Другой'

        __empty__ = '(Выберите тип почты)'

    default_email_type = EmailTypeEnum.PERSONAL

    email = models.EmailField('E-Mail')
    email_type = models.CharField(
        'Тип почты',
        max_length=16,
        choices=EmailTypeEnum.choices,
        blank=False
    )

    def __str__(self):
        return f"{self.email} ({self.get_email_type_display()})"

    class Meta:
        abstract = True
