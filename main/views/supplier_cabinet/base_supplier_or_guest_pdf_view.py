from pathlib import Path

from django.http import FileResponse, Http404

from main.utils.utils import is_valid_pdf
from main.views.supplier_cabinet.base_supplier_or_guest_cabinet_view import BaseSupplierOrGuestCabinetView


class BaseSupplierOrGuestPdfView(BaseSupplierOrGuestCabinetView):
    template_name = None
    user_name = None

    def get(self, request, *args, **kwargs):
        path = Path(self.supplier().agency.reports_path) / self.template_name
        if not is_valid_pdf(str(path)):
            raise Http404("Документ не найден")
        return FileResponse(open(path, "rb"), as_attachment=True, filename=self.user_name)
