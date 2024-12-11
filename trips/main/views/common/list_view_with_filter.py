from django.views.generic import ListView

from main.views.common.multiple_object_with_filter_mixin import MultipleObjectWithFilterMixin


class ListViewWithFilter(MultipleObjectWithFilterMixin, ListView):
    pass
