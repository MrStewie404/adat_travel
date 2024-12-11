from main.models.clients.client import Client
from main.models.trips.accommodation.abstract_trip_roommates_group import AbstractTripRoommatesGroup, \
    AbstractTripRoommatesGroupManager


class TripRoommatesGroupManager(AbstractTripRoommatesGroupManager):
    @staticmethod
    def person_class():
        return Client


class TripRoommatesGroup(AbstractTripRoommatesGroup):
    """Группа туристов - соседей по номеру (т.е. живущих в одном номере в конкретной гостинице)."""
    trip_hotel_visit = AbstractTripRoommatesGroup.create_trip_hotel_visit(related_name='tourist_roommate_groups')
    roommates = AbstractTripRoommatesGroup.create_roommates(person_class=Client, related_name='roommate_groups')

    objects = TripRoommatesGroupManager()

    def natural_key(self):
        return super().natural_key()

    natural_key.dependencies = ['main.triphotelvisit', 'main.client']

    def is_tourists_group(self):
        return True

    def get_all_trip_companies(self):
        companies = set()
        for person in self.roommates.all():
            company = person.get_trip_company(self.trip_hotel_visit.trip)
            if company:
                companies.add(company)
        return companies

    def get_single_related_trip_company(self):
        companies = self.get_all_trip_companies()
        if len(companies) == 1:
            return next(iter(companies))
        return None

    def get_desired_room_type(self):
        from main.models.trips.tourists.trip_company import TripCompany
        desired_room_type = TripCompany.AccommodationTypeEnum.NONE
        related_company = self.get_single_related_trip_company()
        if related_company:
            if related_company.tourists.count() == self.roommates.count():
                desired_room_type = related_company.desired_room_type
            elif related_company.desired_room_type == TripCompany.AccommodationTypeEnum.TWO_DOUBLE_ROOMS:
                # Селим часть такой компании в любой 2-местный номер
                desired_room_type = TripCompany.AccommodationTypeEnum.DOUBLE
        return desired_room_type

    class Meta:
        verbose_name = 'Группа соседей по номеру'
        verbose_name_plural = 'Группы соседей по номерам'
        constraints = AbstractTripRoommatesGroup.Meta.constraints
