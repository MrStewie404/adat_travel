from django.db import models
from django.forms import Form


class BaseFilterFormMixin(Form):
    def validate_and_clean(self, field_name):
        if self.is_valid():
            return self.cleaned_data[field_name]
        return None

    def filter(self, query_set):
        return query_set

    @staticmethod
    def text_filter(query_set, text, fields):
        if text:
            q = models.Q()
            for field in fields:
                kwargs = {f"{field}__icontains": text}
                q = q | models.Q(**kwargs)
            return query_set.filter(q)

        return query_set

    @staticmethod
    def choices_filter(query_set, text, field, choices):
        if text:
            text_lower = text.lower()
            field_lookup = f"{field}__in"
            field_values = [k for k, v in choices if text_lower in v.lower()]
            kwargs = {field_lookup: field_values}
            q = models.Q(**kwargs)
            return query_set.filter(q)

        return query_set
