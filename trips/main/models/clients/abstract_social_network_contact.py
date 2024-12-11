from django.db import models

from main.models.clients.abstract_contact import AbstractContact


class AbstractSocialNetworkContact(AbstractContact):
    """Абстрактная модель: аккаунт в соц. сети."""

    class SocialNetworkTypeEnum(models.TextChoices):
        VK = 'VK', 'ВКонтакте'
        FACEBOOK = 'FACEBOOK', 'Facebook'
        TWITTER = 'TWITTER', 'Twitter'
        SKYPE = 'SKYPE', 'Skype'
        INSTAGRAM = 'INSTAGRAM', 'Instagram'
        OPEN_LINE = 'OPEN_LINE', 'Открытая линия'
        TELEGRAM = 'TELEGRAM', 'Telegram'
        WHATSAPP = 'WHATSAPP', 'WhatsApp'
        OTHER = 'OTHER', 'Другое'

        __empty__ = '(Выберите социальную сеть)'

    account = models.CharField('Аккаунт', max_length=512)
    social_network = models.CharField(
        'Социальная сеть',
        max_length=16,
        choices=SocialNetworkTypeEnum.choices,
        blank=False
    )

    def __str__(self):
        return f"{self.get_social_network_display()}: {self.account}"

    class Meta:
        abstract = True
