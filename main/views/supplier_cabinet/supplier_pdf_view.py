from main.views.supplier_cabinet.base_supplier_cabinet_view import BaseSupplierCabinetView
from main.views.supplier_cabinet.base_supplier_or_guest_pdf_view import BaseSupplierOrGuestPdfView


class SupplierPdfView(BaseSupplierCabinetView, BaseSupplierOrGuestPdfView):
    pass
