from django.db import connection
from django.db.models import IntegerField, ExpressionWrapper
from django.db.models.functions import ExtractDay


def aggregate_subquery(filtered_queryset, aggregate_fun, aggregate_by):
    # См. https://docs.djangoproject.com/en/4.0/ref/models/expressions/#using-aggregates-within-a-subquery-expression
    values_grouped = filtered_queryset.order_by().values(aggregate_by)
    subquery = values_grouped.annotate(aggregate_q=aggregate_fun).values('aggregate_q')
    return subquery


def extract_days_universal(duration_expr):
    """
    Универсальный способ извлечь количество дней из выражения, вычисляющего длительность
    (в sqlite нельзя использовать джанговскую функцию ExtractDays).
    """
    if connection.features.has_native_duration_field:
        return ExtractDay(duration_expr)
    
    microseconds_in_day = 24 * 60 * 60 * 1000 * 1000
    duration_microseconds = ExpressionWrapper(duration_expr, output_field=IntegerField())
    return duration_microseconds / microseconds_in_day


def get_annotated_model(model, annotate_queryset_fun):
    qs = type(model).objects.filter(pk=model.pk)
    return annotate_queryset_fun(qs).first()
