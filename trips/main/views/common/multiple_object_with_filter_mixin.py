from django.views.generic.list import MultipleObjectMixin

from main.forms.common.default_filter_form import DefaultFilterForm
from main.forms.common.default_search_form import DefaultSearchForm
from main.views.common.context_extensions_mixin import ContextExtensionsMixin


class MultipleObjectWithFilterMixin(ContextExtensionsMixin, MultipleObjectMixin):
    filter_form = None
    context_filter_form_name = 'filter_form'
    search_form = None
    context_search_form_name = 'search_form'
    search_form_class = DefaultSearchForm
    paginate_by = 15

    def dispatch(self, request, *args, **kwargs):
        self.init_filter_search_forms()
        return super().dispatch(request, *args, **kwargs)

    def init_filter_search_forms(self):
        self.filter_form = self.get_filter_form()
        self.search_form = self.get_search_form()

    def get_filter_form(self):
        return DefaultFilterForm(self.request)

    def get_search_form(self):
        return self.search_form_class(self.get_search_form_data())

    def get_search_form_data(self):
        return self.request.GET

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)

        if self.paginate_by:
            paginator = context['page_obj'].paginator
            self.filter_form.fields['page'].choices = [(x, x) for x in range(1, paginator.num_pages + 1)]

        # Add in the custom
        if self.context_filter_form_name:
            context[self.context_filter_form_name] = self.filter_form
            if self.filter_form and [k for k, v in self.filter_form.data.items() if v and k != 'page']:
                context['is_filtered'] = True
        if self.context_search_form_name:
            context[self.context_search_form_name] = self.search_form
        if hasattr(self.filter_form, "active_sidebar_item"):
            active = self.filter_form.active_sidebar_item()
            # Установка подсвеченного пункта меню при использовании шаблона
            # main/templates/main/snippets/sidebar/s_base_sidebar_menu_item.html
            context['active_sidebar_item'] = active
        return context
