import datetime
from decimal import Decimal

from django.http import JsonResponse

from main.templatetags.format_extensions import currency
from main.utils.utils import int_or_default
from main.views.supplier_cabinet.base_supplier_or_guest_trip_booking_view import BaseSupplierOrGuestTripBookingView


# TODO: вместо этого View нужно сделать TemplateView, который будет выдавать готовый html с деталями тура
class BaseSupplierOrGuestGetTripInfoView(BaseSupplierOrGuestTripBookingView):
    year_get_kwarg = 'y'
    month_get_kwarg = 'm'
    day_get_kwarg = 'd'
    tourists_count_get_kwarg = 'count'

    def get(self, request, *args, **kwargs):
        if request.is_ajax():
            y = int_or_default(request.GET.get(self.year_get_kwarg))
            m = int_or_default(request.GET.get(self.month_get_kwarg))
            d = int_or_default(request.GET.get(self.day_get_kwarg))
            tourists_count = int_or_default(request.GET.get(self.tourists_count_get_kwarg))
            if y is not None and m is not None and d is not None and tourists_count is not None:
                date = datetime.date(y, m, d)
                trip = self.route_trips.filter(start_date=date).first()
                if trip:
                    contract_price = tourists_count * trip.price
                    commission = self.supplier().calc_default_commission(contract_price)
                    total_prepayment = tourists_count * trip.default_prepayment
                    price_per_tourist_str = f"{currency(trip.price, 0)}\u00A0₽\u00A0за\u00A01\u00A0гостя"

                    if trip.default_prepayment < 0.01:
                        prepayment_per_tourist_str = "Без предоплаты"
                    elif round(trip.default_prepayment, 2) >= round(trip.price, 2):
                        prepayment_per_tourist_str = "100% предоплата"
                    else:
                        prepayment_per_tourist_str = f"Предоплата\u00A0{currency(trip.default_prepayment, 0)}\u00A0₽\u00A0за\u00A01\u00A0гостя"

                    total_price_str = f"{currency(contract_price, 0)}\u00A0₽"

                    if total_prepayment < 0.01:
                        total_prepayment_str = ""
                    else:
                        total_prepayment_str = f"Предоплата {currency(total_prepayment, 0)}\u00A0₽"

                    departure_point_pks = [x.pk for x in trip.departure_points.all()]

                    return JsonResponse({
                        'price_per_tourist_str': price_per_tourist_str,
                        'commission': commission,
                        'free_seats_count': trip.free_seats_count(),
                        'prepayment_per_tourist_str': prepayment_per_tourist_str,
                        'total_price_str': total_price_str,
                        'total_prepayment_str': total_prepayment_str,
                        'departure_point_pks': departure_point_pks,
                    }, status=200)

        return JsonResponse({}, status=400)
