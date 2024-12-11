from pathlib import Path

from django.apps import apps
from django.views.debug import ExceptionReporter


class EmailExceptionReporter(ExceptionReporter):
    @property
    def text_template_path(self):
        return Path(apps.get_app_config('main').path) / 'templates' / 'email_technical_500.txt'
