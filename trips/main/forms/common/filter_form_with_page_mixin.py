from django.forms import CharField

from main.forms.common.base_filter_form_mixin import BaseFilterFormMixin
from main.forms.common.widgets import select
from main.utils.utils import int_or_default


class FilterFormWithPageMixin(BaseFilterFormMixin):
    page = CharField(
        widget=select(submit=True),
        label='',
        required=False,
    )

    def clean_page(self):
        page = self.validate_and_clean('page')
        if page is None:
            return None
        return int_or_default(page)
