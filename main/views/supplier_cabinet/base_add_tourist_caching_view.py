from django.views.generic.edit import BaseFormView


class BaseAddTouristCachingView(BaseFormView):
    prev_data_session_key = 'prev_company_data'
    fields_to_cache = ["name", "surname", "last_name", "phone_number", "tourists_count"]
    fill_initial_from_prev_data = True

    def dispatch(self, request, *args, **kwargs):
        self.prev_company_data = self.get_company_data_from_session()
        return super().dispatch(request, *args, **kwargs)

    def get_initial(self):
        initial = super().get_initial()
        prev_company = self.prev_company_data
        if prev_company and self.fill_initial_from_prev_data:
            initial.update(prev_company)
        return initial

    def form_valid(self, form):
        self.save_company_in_session(form)
        return super(self).form_valid(form)

    def save_company_in_session(self, form):
        session_data = {key: form.cleaned_data.get(key) for key in self.fields_to_cache}
        self.request.session[self.prev_data_session_key] = session_data

    def get_company_data_from_session(self):
        return self.request.session.get(self.prev_data_session_key)
