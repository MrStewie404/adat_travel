from main.views.media.simple_image_serve_view import SimpleImageServeView
from main.views.supplier_cabinet.base_supplier_cabinet_view import BaseSupplierCabinetView


class SupplierCabinetImageServeView(SimpleImageServeView, BaseSupplierCabinetView):
    pass
