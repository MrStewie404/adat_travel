import datetime
from calendar import monthrange
from collections import OrderedDict

from crispy_forms.helper import FormHelper
from django.forms import ChoiceField, DateField

from main.forms.common.filter_form_with_page_mixin import FilterFormWithPageMixin
from main.forms.common.widgets import select, date_input
from main.utils.utils import get_month_name, int_or_default


class DateFilterFormMixin(FilterFormWithPageMixin):
    month = ChoiceField(
        choices=(),
        widget=select(width="100%"),
        label='',
        required=False,
    )

    start_date = DateField(required=False, widget=date_input('C или пусто', width="100%"), label='C даты')
    end_date = DateField(required=False, widget=date_input('По или пусто',  width="100%"), label='По дату')

    # Установите True если хотите использовать в фильтре даты и подключите скрипт pages/common/dates_filter.js
    use_dates_filter = False

    helper = FormHelper()
    helper.form_show_labels = False

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['month'].choices = self.month_choices()
        if self.use_dates_filter:
            self.fields['month'].widget.attrs.update({'class': 'form-control js-submit-month'})

    @property
    def first_date_filter(self):
        """Переопределите этот метод, чтобы он возвращал правильную минимальную дату"""
        return datetime.date.today()

    @property
    def last_date_filter(self):
        """Переопределите этот метод, чтобы он возвращал правильную максимальную дату"""
        return datetime.date.today()

    @property
    def first_date_query(self):
        if self.is_valid() and self.cleaned_data['start_date']:
            return self.cleaned_data['start_date']

        return self.first_date_filter

    @property
    def last_date_query(self):
        if self.is_valid() and self.cleaned_data['end_date']:
            return self.cleaned_data['end_date']

        return self.last_date_filter

    def month_choices(self):
        return self.month_range_to_list(self.month_range(self.first_date_filter, self.last_date_filter))

    def clean_month(self):
        return self.validate_and_clean('month')

    def do_filter_by_month(self, query_set, month_str, date_field_name, date_field_name_for_first_last_date=None):
        date_field_name_for_first_last_date = date_field_name_for_first_last_date or date_field_name
        filter_kwargs = {
            f"{date_field_name_for_first_last_date}__gte": self.first_date_query,
            f"{date_field_name_for_first_last_date}__lte": self.last_date_query,
        }
        if month_str is not None:
            try:
                filter_value = datetime.datetime.strptime(month_str, "%Y_%m").date()
                filter_kwargs[f"{date_field_name}__year"] = filter_value.year
                filter_kwargs[f"{date_field_name}__month"] = filter_value.month
                return query_set.filter(**filter_kwargs)
            except ValueError:
                year = int_or_default(month_str)
                if year is not None:
                    filter_kwargs[f"{date_field_name}__year"] = year
                    return query_set.filter(**filter_kwargs)

        return query_set.filter(**filter_kwargs)

    @staticmethod
    def month_range_to_list(year_month_grouped):
        year_list = [('', '(Любой месяц)')]
        for year, months in year_month_grouped.items():
            month_list = [(f"{year}", f"Все в {year}")] + [(f"{year}_{x}", get_month_name(x) + " " + str(year)) for x in
                                                           months]
            year_list += [(year, month_list)]
        return year_list

    @staticmethod
    def month_range(first_date, last_date):
        year_month_grouped = OrderedDict()
        last_date = last_date.replace(day=monthrange(last_date.year, last_date.month)[1])
        while first_date <= last_date:
            months = year_month_grouped.setdefault(first_date.year, [])
            months.append(first_date.month)
            first_date += datetime.timedelta(days=monthrange(first_date.year, first_date.month)[1])
        return year_month_grouped
