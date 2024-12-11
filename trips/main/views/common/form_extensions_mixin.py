from django.views.generic.edit import FormMixin

from main.views.common.context_extensions_mixin import ContextExtensionsMixin


class FormExtensionsMixin(ContextExtensionsMixin, FormMixin):
    """Добавляет часто используемые в наших вьюхах-формах поля и методы."""
    cancel_url = None

    def get_cancel_url(self):
        """Возвращает url для перехода по кнопке Отмена."""
        return self.cancel_url

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['on_cancel_url'] = self.get_cancel_url()
        return context
