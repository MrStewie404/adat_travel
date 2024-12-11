from datetime import timedelta, date

from django.urls import reverse

from main.forms.supplier_cabinet.supplier_add_tourist_form import SupplierAddTouristForm
from main.views.common.previous_page_mixin import PreviousPageMixin
from main.views.supplier_cabinet.base_supplier_cabinet_view import BaseSupplierCabinetView
from main.views.supplier_cabinet.base_supplier_or_guest_add_tourist_view import BaseSupplierOrGuestAddTouristView


class AddTouristView(BaseSupplierCabinetView, BaseSupplierOrGuestAddTouristView, PreviousPageMixin):
    form_class = SupplierAddTouristForm
    template_name = 'main/supplier_cabinet/tourist_add.html'
    fill_initial_from_prev_data = False
    tomorrow_field_name = 'tomorrow'

    def show_prev_tourist_link(self):
        return self.prev_company_data is not None

    def is_tomorrow_date(self):
        return self.request.GET.get(self.tomorrow_field_name, '') == 'true'

    def get_initial_tourists_count(self):
        return 1

    def get_page_title(self):
        return 'Добавление гостей'

    def get_initial(self):
        initial = super().get_initial()
        tourists_count = self.get_initial_tourists_count()
        min_contract_price = tourists_count * self.min_trip_price()
        commission = self.supplier().calc_default_commission(min_contract_price)
        trip_date = date.today() + timedelta(days=1) if self.is_tomorrow_date() else None
        initial.update({
            'tourists_count': tourists_count,
            'supplier_commission': commission,
            'trip_date': trip_date,
        })
        return initial

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['show_prev_tourist_link'] = self.show_prev_tourist_link()
        guest_cabinet = self.get_supplier_cabinet_link().try_get_guest_cabinet()
        context['guest_cabinet_id'] = guest_cabinet.cabinet_id if guest_cabinet else '???'
        return context

    def save_tourist(self, form, supplier):
        return form.save_as_new_or_existing_tourist(supplier)

    def get_previous_url(self):
        return super().get_previous_url() or reverse(
            'supplier_lk_excursions' if self.route.is_excursion else 'supplier_lk_multi_day_trips',
            kwargs={'cabinet_id': self.cabinet_id}
        )

    def get_success_url(self):
        return self.get_previous_url()

    def get_cancel_url(self):
        return self.get_previous_url()
