from datetime import timedelta, datetime, date

from django.core.mail import send_mail
from django.template.backends.django import DjangoTemplates

from main.models.clients.abstract_email_contact import AbstractEmailContact
from main.utils.home_folder import HomeFolder


def send_info_mail(contract):
    email_to = contract.customer.emails.filter(email_type=AbstractEmailContact.default_email_type).last()
    if not email_to:
        return

    trip = contract.trip_company.trip
    agency = trip.agency
    meeting_time = (datetime.combine(date.min.replace(day=2), trip.start_time) - timedelta(minutes=20)).time() \
        if trip.start_time else None
    ctx = {
        'trip': trip,
        'agency': agency,
        'contract': contract,
        'meeting_time': meeting_time,
    }

    mails_path = agency.mails_path
    mails_path_alt = HomeFolder.default_folder().path_mails
    engine = DjangoTemplates({
        'NAME': 'custom',
        'DIRS': [mails_path, mails_path_alt],
        'APP_DIRS': False,
        'OPTIONS': {},
    })
    plain_message = engine.get_template('info_mail.txt').render(context=ctx)
    html_message = engine.get_template('info_mail.html').render(context=ctx)

    subject = "ПОДТВЕРЖДЕНИЕ БРОНИРОВАНИЯ"

    send_mail(subject, plain_message, None, [email_to], fail_silently=False, html_message=html_message)
