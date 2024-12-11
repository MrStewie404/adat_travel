from main.forms.common.filter_form_with_page_mixin import FilterFormWithPageMixin


class DefaultFilterForm(FilterFormWithPageMixin):
    """Форма фильтрации по умолчанию. На самом деле ничего не фильтрует, а нужна только для хранения номера страницы."""
    def __init__(self, request):
        if not list(request.GET.items()):
            super().__init__()
        else:
            super().__init__(data=request.GET)
