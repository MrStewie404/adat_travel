from django.views.generic import CreateView
from django.views.generic.edit import ModelFormMixin

from main.models.clients.client import Client
from main.views.common.form_extensions_mixin import FormExtensionsMixin
from main.views.supplier_cabinet.base_add_tourist_caching_view import BaseAddTouristCachingView
from main.views.supplier_cabinet.base_supplier_or_guest_trip_booking_view import BaseSupplierOrGuestTripBookingView
from main.views.supplier_cabinet.supplier_or_guest_cabinet_context_mixin import \
    SupplierOrGuestCabinetContextMixin


class BaseSupplierOrGuestAddTouristView(BaseSupplierOrGuestTripBookingView, SupplierOrGuestCabinetContextMixin,
                                        FormExtensionsMixin, BaseAddTouristCachingView, CreateView):
    model = Client

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['agency'] = self.supplier().agency
        kwargs['trips_queryset'] = self.route_trips
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        route = self.route
        context['route'] = route
        context['min_trip_price'] = self.min_trip_price()
        context['has_different_prices'] = self.has_different_prices()
        context['valid_dates_info'] = [{
            'date_str': trip.start_date.strftime('%d.%m.%Y'),
            'free_seats': trip.free_seats_count(),
        } for trip in self.route_trips]
        return context

    def form_valid(self, form):
        supplier = self.supplier()
        self.object, self.company = self.save_tourist(form, supplier)
        self.save_company_in_session(form)
        return super(ModelFormMixin, self).form_valid(form)

    def save_tourist(self, form, supplier):
        return form.save_as_new_or_existing_tourist(supplier)
