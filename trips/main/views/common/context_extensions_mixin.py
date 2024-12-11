from django.views.generic.base import ContextMixin

from main.business_logic.warnings.agency_warnings_provider import AgencyWarningsProvider
from main.views.common.permission_helper_mixin import PermissionHelperMixin


class ContextExtensionsMixin(PermissionHelperMixin, ContextMixin):
    """Добавляет в контекст часто используемые в наших вьюхах параметры."""
    page_title = None

    def get_page_title(self):
        """Заголовок страницы."""
        return self.page_title

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = self.get_page_title()
        context['permissions'] = self.permission_helper.permissions
        if self.request.user_agency:
            context['agency_warnings'] = AgencyWarningsProvider(self.request.user_agency).get_warnings()
        return context
