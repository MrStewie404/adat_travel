import json
import logging

from django.db import transaction
from django.http import HttpResponse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from yookassa.domain.notification import WebhookNotification

from main.business_logic.info_mails import send_info_mail
from main.models.money.agency_payment_token import PaymentSystemChoicesEnum
from main.models.money.draft_contract_payment import DraftContractPayment


@method_decorator(csrf_exempt, name='dispatch')
class YookassaWebhookView(View):
    valid_ip_list = [
        '185.71.76.0/27',
        '185.71.77.0/27',
        '77.75.153.0/25',
        '77.75.156.11',
        '77.75.156.35',
        '77.75.154.128/25',
        '2a02:5180::/32',
    ]

    # TODO: написать тесты
    def post(self, request, *args, **kwargs):
        # Закомментировал, потому что сделана проверка на уровне nginx
        # TODO: на уровне nginx пока не заработало
        # ip, error_msg = self.get_client_ip(self.valid_ip_list)
        # if error_msg:
        #     logging.error(error_msg)
        #     return HttpResponse(status=400)

        event_json = json.loads(request.body)
        try:
            notification_object = WebhookNotification(event_json)
        except Exception:
            logging.error("Failed to parse webhook notification")
            return HttpResponse(status=400)

        payment = notification_object.object
        if not payment:
            logging.error("Webhook notification object is empty")
            return HttpResponse(status=400)

        draft_payment = DraftContractPayment.objects.filter(
            payment_id=payment.id,
            payment_token__payment_system=PaymentSystemChoicesEnum.YOOKASSA,
        ).first()
        if draft_payment:
            if round(payment.amount.value, 2) != round(draft_payment.amount, 2):
                logging.error(f"Unexpected payment amount. Expected {draft_payment.amount}, got {payment.amount.value}.")
                return HttpResponse(status=400)
            if notification_object.event == "payment.succeeded" and payment.status == "succeeded":
                contract = draft_payment.client_contract
                # supplier = contract.trip_company.supplier
                with transaction.atomic():
                    contract.add_payment(
                        owner=None,
                        payment_amount=draft_payment.amount,
                        contract_part_amount=draft_payment.amount,
                        is_prepayment=True,
                        payment_date=draft_payment.created_at.date(),
                        account=None,
                    )
                    draft_payment.delete()
                send_info_mail(contract)
            elif notification_object.event == "payment.cancelled" and payment.status == "cancelled":
                draft_payment.delete()
        return HttpResponse(status=200)

    def get_client_ip(self, trusted_ips):
        # TODO: возможно, небезопасный способ (см. https://esd.io/blog/flask-apps-heroku-real-ip-spoofing.html)
        x_forwarded_for = self.request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ips = x_forwarded_for.split(',')
            if len(ips) != 1:
                return None, f"More than one proxy address found: {x_forwarded_for}"
            ip = ips[0]
        else:
            ip = self.request.META.get('REMOTE_ADDR')
        if ip not in trusted_ips:
            return None, f"Untrusted IP: {ip}"
        return ip, None
