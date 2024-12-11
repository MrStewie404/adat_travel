from main.views.supplier_cabinet.add_tourist_view import AddTouristView


class AddPrevTouristView(AddTouristView):
    fill_initial_from_prev_data = True

    def show_prev_tourist_link(self):
        return False

    def get_initial_tourists_count(self):
        if self.prev_company_data:
            return self.prev_company_data['tourists_count']
        return super().get_initial_tourists_count()
