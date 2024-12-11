from django.urls import reverse

from main.forms.clients.guest_cabinet.add_tourist_form import AddTouristForm
from main.models.money.draft_contract_payment import DraftContractPayment
from main.views.guest_cabinet.base_guest_cabinet_view import BaseGuestCabinetView
from main.views.supplier_cabinet.base_supplier_or_guest_add_tourist_view import BaseSupplierOrGuestAddTouristView


class AddTouristView(BaseGuestCabinetView, BaseSupplierOrGuestAddTouristView):
    form_class = AddTouristForm
    template_name = 'main/guest_cabinet/tourist_add.html'

    def get_page_title(self):
        return 'Запись на тур'

    def save_tourist(self, form, supplier):
        return form.save_as_new_or_existing_tourist(supplier)

    def get_success_url(self):
        contract = self.company.try_get_client_contract()
        if not contract:
            raise RuntimeError("Client contract not found")
        default_url = reverse('guest_lk_thanks', kwargs={'cabinet_id': self.cabinet_id, 'contract_slug': contract.slug})
        agency = self.supplier().agency
        payment_token = agency.try_get_payment_token()
        if payment_token and contract.prepayment:
            return_url = self.request.build_absolute_uri(default_url)
            return self.get_external_payment_url(payment_token, contract, return_url)
        return default_url

    @staticmethod
    def get_external_payment_url(payment_token, contract, return_url):
        return AddTouristView.get_yookassa_payment_url(payment_token, contract, return_url)

    @staticmethod
    def get_yookassa_payment_url(payment_token, contract, return_url):
        from yookassa import Configuration, Payment
        import uuid

        Configuration.account_id = payment_token.account_id
        Configuration.secret_key = payment_token.secret_key

        company = contract.trip_company
        amount = contract.prepayment
        payment = Payment.create({
            "amount": {
                "value": str(amount),
                "currency": "RUB",
            },
            "confirmation": {
                "type": "redirect",
                "return_url": return_url,
            },
            "capture": True,
            "description": f"Аванс за тур {company.trip} ({company.get_customer().signature_initials()})",
        }, uuid.uuid4())
        DraftContractPayment.objects.create(
            payment_token=payment_token, client_contract=contract, payment_id=payment.id, amount=amount,
        )
        return payment.confirmation.confirmation_url

    def get_cancel_url(self):
        return reverse('guest_lk_dashboard', kwargs={'cabinet_id': self.cabinet_id})
