from django.http import Http404, JsonResponse, HttpResponse

from main.views.supplier_cabinet.base_supplier_cabinet_view import BaseSupplierCabinetView


class GuestCabinetGetOrCreateView(BaseSupplierCabinetView):
    def post(self, request, *args, **kwargs):
        if not request.is_ajax():
            return JsonResponse({}, status=400)

        url = self.try_get_guest_cabinet_url(create_if_absent=True)
        if not url:
            raise Http404("Нельзя создать ссылку для самозаписи.")
        return HttpResponse(url, status=200)
