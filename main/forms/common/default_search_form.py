from django.forms import CharField

from main.forms.common.base_filter_form_mixin import BaseFilterFormMixin
from main.forms.common.widgets import search_text_input


class DefaultSearchForm(BaseFilterFormMixin):
    """
    Форма поиска по умолчанию. Выполняет поиск по введённой строке
    (в конструктор можно передать произвольный список полей, по которым будет идти фильтрация).
    """
    name = CharField(
        widget=search_text_input(),
        label='',
        required=False,
    )

    default_filter_fields = ['name']
    default_distinct = False

    def __init__(self, *args, **kwargs):
        self.filter_fields = kwargs.pop('filter_fields', self.default_filter_fields)
        self.distinct = kwargs.pop('distinct', self.default_distinct)
        super().__init__(*args, **kwargs)

    def clean_name(self):
        return self.validate_and_clean('name')

    def filter(self, query_set):
        query_set = BaseFilterFormMixin.text_filter(query_set, self.clean_name(), fields=self.filter_fields)
        if self.distinct:
            query_set = query_set.distinct()
        return query_set
