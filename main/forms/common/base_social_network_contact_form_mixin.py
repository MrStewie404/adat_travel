from django.core.exceptions import ImproperlyConfigured
from django.forms import Form, ChoiceField, CharField

from main.forms.common.widgets import select, text_input
from main.models.clients.abstract_social_network_contact import AbstractSocialNetworkContact
from main.validators.social_network_account_validator import validate_social_network_account


class BaseSocialNetworkContactFormMixin(Form):
    """
    Mixin для форм, добавляет поля для ввода аккаунта и выбора соц. сети, сохраняет их в отдельную модель.
    Поддерживает только один аккаунт одного типа, все остальные автоматически удаляет при сохранении аккаунта.
    """
    social_network_contact = CharField(widget=text_input('Аккаунт'), label='Аккаунт', required=False)
    social_network_contact_type = ChoiceField(
        choices=AbstractSocialNetworkContact.SocialNetworkTypeEnum.choices,
        widget=select(width='100%', height=35),
        label='Социальная сеть',
        initial=AbstractSocialNetworkContact.SocialNetworkTypeEnum.TELEGRAM,
        required=True,
    )

    social_network_contact_model = None
    social_network_contact_foreign_key_name = ''
    social_network_contact_related_name = 'social_network_contacts'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        contact_inst = None
        if self.instance.pk:
            contact_inst = getattr(self.instance, self.social_network_contact_related_name).first()
        if contact_inst:
            self.initial['social_network_contact'] = contact_inst.account
            self.initial['social_network_contact_type'] = contact_inst.social_network

    def clean_social_network_contact(self):
        account = self.cleaned_data.get('social_network_contact')
        if account:
            validate_social_network_account(account)
        return account

    def save_or_delete_social_network_contact(self, account_name, social_network):
        if not self.social_network_contact_model:
            raise ImproperlyConfigured("A social_network_contact_model is required.")
        if not self.social_network_contact_foreign_key_name:
            raise ImproperlyConfigured("A social_network_contact_foreign_key_name is required.")
        owner = self.instance
        contact_inst = getattr(owner, self.social_network_contact_related_name).filter(
            social_network=social_network,
            account=account_name,
        ).first()
        contact_pk = contact_inst.pk if contact_inst else None
        # Удаляем все другие аккаунты
        getattr(owner, self.social_network_contact_related_name).exclude(pk=contact_pk).delete()
        if account_name and not contact_inst:
            create_kwargs = {
                self.social_network_contact_foreign_key_name: owner,
                'social_network': social_network,
                'account': account_name,
            }
            self.social_network_contact_model.objects.create(**create_kwargs)

    class Meta:
        fields = ['social_network_contact', 'social_network_contact_type']
