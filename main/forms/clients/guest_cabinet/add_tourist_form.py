from main.forms.supplier_cabinet.base_add_tourist_form import BaseAddTouristForm


class AddTouristForm(BaseAddTouristForm):
    supplier_commission = None
    is_commission_paid = None

    class Meta(BaseAddTouristForm.Meta):
        fields = ['surname', 'name', 'middle_name', 'phone_number', 'tourists_count', 'has_children_pre7',
                  'agree_with_policies']
