from main.models.trips.accommodation.abstract_trip_roommates_group import AbstractTripRoommatesGroup, \
    AbstractTripRoommatesGroupManager
from main.models.workers.trip_worker import TripWorker


class TripWorkerRoommatesGroupManager(AbstractTripRoommatesGroupManager):
    @staticmethod
    def person_class():
        return TripWorker


class TripWorkerRoommatesGroup(AbstractTripRoommatesGroup):
    """Группа водителей/гидов - соседей по номеру."""
    trip_hotel_visit = AbstractTripRoommatesGroup.create_trip_hotel_visit(related_name='worker_roommate_groups')
    roommates = AbstractTripRoommatesGroup.create_roommates(person_class=TripWorker, related_name='roommate_groups')

    objects = TripWorkerRoommatesGroupManager()

    def natural_key(self):
        return super().natural_key()

    natural_key.dependencies = ['main.triphotelvisit', 'main.tripworker']

    def __str__(self):
        return f"Trip worker roommates ({self.trip_hotel_visit})"

    def is_tourists_group(self):
        return False

    class Meta:
        verbose_name = 'Группа водителей/гидов - соседей по номеру'
        verbose_name_plural = 'Группы водителей/гидов - соседей по номерам'
        constraints = AbstractTripRoommatesGroup.Meta.constraints
