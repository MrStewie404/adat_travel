from main.forms.supplier_cabinet.base_add_tourist_form import BaseAddTouristForm


class SupplierAddTouristForm(BaseAddTouristForm):
    agree_with_policies = None

    class Meta(BaseAddTouristForm.Meta):
        exclude = ['agree_with_policies']
