from functools import reduce
from itertools import chain

from django.db import transaction

import main.models.trips.tourists.trip_company
import main.models.hotels.hotel_room_type
from main.models.clients.abstract_person import AbstractPerson
from main.models.trips.accommodation.trip_worker_roommates_group import TripWorkerRoommatesGroup
from main.models.trips.accommodation.trip_roommates_group import TripRoommatesGroup
from main.business_logic.trip_accommodation_utils import make_roommate_pairs, cleanup_hotel_visit, reserve_room
from main.business_logic.trip_company_utils import cleanup_trip_companies

AccommodationTypeEnum = main.models.trips.tourists.trip_company.TripCompany.AccommodationTypeEnum
RoomTypeEnum = main.models.hotels.hotel_room_type.HotelRoomType.RoomTypeEnum


class TripAutoAccommodationHelper:

    class AccommodationResult:
        def __init__(self):
            self.optimized_groups = []
            self.skipped_groups = []
            self.new_accommodated_groups = []
            self.not_accommodated_groups = []

        def optimized_tourists_count(self):
            return sum(x.roommates_count() for x in self.optimized_groups)

        def skipped_groups_count(self):
            return len(self.skipped_groups)

        def new_accommodated_groups_count(self):
            return len(self.new_accommodated_groups)

        def not_accommodated_groups_count(self):
            return len(self.not_accommodated_groups)

    def __init__(self, hotel_visit):
        self.hotel_visit = hotel_visit

    @property
    def trip(self):
        return self.hotel_visit.trip

    def auto_accommodate(self):
        """
        Автоматически расселяет туристов и работников по доступным номерам,
        по возможности попарно объединяя одиночных туристов и работников по полу и возрасту.
        """
        with transaction.atomic():
            result = self.AccommodationResult()
            cleanup_trip_companies(self.trip)
            cleanup_hotel_visit(self.hotel_visit)
            result.optimized_groups = self.optimize_accommodation()
            tourist_groups_iter = self.sorted_roommate_groups(self.hotel_visit.tourist_roommate_groups.all())
            worker_groups_iter = self.sorted_roommate_groups(self.hotel_visit.worker_roommate_groups.all())
            for group in chain(tourist_groups_iter, worker_groups_iter):
                if group.try_get_room_reservation() or not group.is_room_needed:
                    result.skipped_groups.append(group)
                    continue
                is_succeeded = self.auto_accommodate_roommates(group)
                if is_succeeded:
                    result.new_accommodated_groups.append(group)
                else:
                    result.not_accommodated_groups.append(group)
            for booking in self.hotel_visit.pre_bookings.all():
                booking.update_status()
        return result

    def auto_accommodate_roommates(self, roommates_group):
        """
        Пытается автоматически заселить группу туристов/работников в один из доступных номеров.
        Возвращает флаг успеха/неуспеха.
        """
        if roommates_group.try_get_room_reservation():
            return False
        desired_room_type = roommates_group.get_desired_room_type()
        available_rooms = set()
        pre_bookings_by_room = dict()
        for booking in self.hotel_visit.pre_bookings.all():
            for room_type in booking.available_room_types(self.hotel_visit.start_date, self.hotel_visit.end_date):
                available_rooms.add(room_type)
                if room_type not in pre_bookings_by_room:
                    pre_bookings_by_room[room_type] = booking
        room_type = self.get_optimal_room_type(
            tourists_count=roommates_group.roommates.count(),
            desired_room_type=desired_room_type,
            all_room_types=available_rooms
        )
        if room_type:
            reserve_room(roommates_group, pre_bookings_by_room[room_type], room_type)
        return room_type is not None

    def sorted_roommate_groups(self, roommate_groups):
        return reversed(sorted(roommate_groups, key=lambda x: x.roommates.count()))

    def optimize_accommodation(self):
        """
        Группирует одиночных туристов/работников по двое (по полу и возрасту) в один номер.
        Возвращает список созданных групп.
        """
        groups = self.optimize_tourists_accommodation()
        groups.extend(self.optimize_workers_accommodation())
        return groups

    def optimize_tourists_accommodation(self):
        """
        Группирует одиночных туристов по двое (по полу и возрасту) в один номер.
        Возвращает список созданных групп.
        """
        tourists_to_join = []
        for group in self.hotel_visit.tourist_roommate_groups.all():
            if group.roommates.count() == 1 and not group.try_get_room_reservation() and group.is_room_needed:
                tourist = group.roommates.first()
                company = tourist.get_trip_company(self.hotel_visit.trip)
                may_join = not company or \
                    company.tourists.count() != 1 or \
                    company.desired_room_type in \
                    (AccommodationTypeEnum.NONE, AccommodationTypeEnum.SINGLE_WITH_SHARING)
                if may_join:
                    tourists_to_join.append(tourist)
        return self.optimize_accommodation_for(persons=tourists_to_join, group_class=TripRoommatesGroup)

    def optimize_workers_accommodation(self):
        """Группирует работников по двое (по полу и возрасту) в один номер. Возвращает список созданных групп."""
        workers_to_join = []
        for group in self.hotel_visit.worker_roommate_groups.all():
            if group.roommates.count() == 1 and group.is_room_needed:
                workers_to_join.append(group.roommates.first())
        return self.optimize_accommodation_for(persons=workers_to_join, group_class=TripWorkerRoommatesGroup)

    def optimize_accommodation_for(self, persons, group_class):
        """
        Группирует указанных туристов или работников по двое (по полу и возрасту) в один номер.
        Возвращает список созданных групп.
        """
        men_to_join = []
        women_to_join = []
        for person in persons:
            # Пол также может быть пустым, таких персон пропускаем.
            if person.sex == AbstractPerson.SexEnum.MALE:
                men_to_join.append(person)
            elif person.sex == AbstractPerson.SexEnum.FEMALE:
                women_to_join.append(person)
        groups = make_roommate_pairs(men_to_join, self.hotel_visit, group_class)
        groups.extend(make_roommate_pairs(women_to_join, self.hotel_visit, group_class))
        return groups

    @staticmethod
    def get_optimal_room_type(tourists_count, desired_room_type, all_room_types):
        """Возвращает оптимальный тип номера по заданным параметрам компании гостей.
        Если подходящего типа номера нет, возвращает None.
        """
        reduce_fun = \
            (lambda a, b:
             a if a and TripAutoAccommodationHelper.is_room_compatible(a.room_type, desired_room_type, tourists_count)
                  and (a.max_adults_count < b.max_adults_count or
                       (a.max_adults_count == b.max_adults_count and
                        TripAutoAccommodationHelper.is_first_room_preferable(a, b, desired_room_type)))
             else (b if (TripAutoAccommodationHelper.is_room_compatible(b.room_type, desired_room_type, tourists_count) and
                         b.min_adults_count <= tourists_count <= b.max_adults_count) else None))
        return reduce(reduce_fun, all_room_types, None)

    @staticmethod
    def is_room_compatible(room_type, desired_room_type, tourists_count):
        """Проверяет, совместим ли тип номера с пожеланиями клиентов
        (предполагается, что проверка на вместимость номера уже прошла).
        """
        if desired_room_type == AccommodationTypeEnum.SINGLE:
            return tourists_count == 1

        if desired_room_type == AccommodationTypeEnum.SINGLE_WITH_SHARING:
            return tourists_count == 1 or \
                   room_type not in (RoomTypeEnum.SINGLE_BIG_BED,
                                     RoomTypeEnum.DOUBLE_BIG_BED,
                                     RoomTypeEnum.TRIPLE_BIG_BED)

        if desired_room_type == AccommodationTypeEnum.SINGLE_BIG_BED:
            # Это у нас такой взыскательный турист; если ему дать номер без большой кровати - может начать шуметь :)
            return tourists_count == 1 and \
                   room_type in (RoomTypeEnum.SINGLE_BIG_BED, RoomTypeEnum.DOUBLE_BIG_BED, RoomTypeEnum.TRIPLE_BIG_BED)

        if desired_room_type == AccommodationTypeEnum.DOUBLE:
            return True

        if desired_room_type == AccommodationTypeEnum.DOUBLE_TWIN_BEDS:
            return room_type not in (RoomTypeEnum.SINGLE_BIG_BED,
                                     RoomTypeEnum.DOUBLE_BIG_BED,
                                     RoomTypeEnum.TRIPLE_BIG_BED)

        if desired_room_type == AccommodationTypeEnum.DOUBLE_BIG_BED:
            return room_type not in (RoomTypeEnum.DOUBLE_TWIN_BEDS, RoomTypeEnum.TRIPLE_THREE_BEDS)

        if desired_room_type == AccommodationTypeEnum.TRIPLE:
            return True

        if desired_room_type == AccommodationTypeEnum.TRIPLE_THREE_BEDS:
            return room_type not in (RoomTypeEnum.DOUBLE_BIG_BED, RoomTypeEnum.TRIPLE_BIG_BED)

        if desired_room_type == AccommodationTypeEnum.TRIPLE_BIG_BED:
            return room_type not in (RoomTypeEnum.DOUBLE_TWIN_BEDS, RoomTypeEnum.TRIPLE_THREE_BEDS)

        if desired_room_type == AccommodationTypeEnum.QUAD:
            return True

        if desired_room_type == AccommodationTypeEnum.TWO_DOUBLE_ROOMS:
            # Таких туристов нельзя селить в один номер, их надо разделить на две группы
            return False

        # По умолчанию не селим в номера с большой кроватью, если предпочтения туристов неизвестны
        return tourists_count == 1 or \
            room_type not in (RoomTypeEnum.SINGLE_BIG_BED, RoomTypeEnum.DOUBLE_BIG_BED, RoomTypeEnum.TRIPLE_BIG_BED)

    @staticmethod
    def is_first_room_preferable(room1, room2, desired_room_type):
        """Проверяет, является ли заселение первого номера более предпочтительным, при прочих равных
        (предполагается, что проверка на вместимость номера уже прошла).
        """
        # По умолчанию сначала заселяем самые маломестные номера (также универсальные номера считаются более ценными)
        ordered_types = (RoomTypeEnum.SINGLE, RoomTypeEnum.DOUBLE_TWIN_BEDS, RoomTypeEnum.DOUBLE_UNIVERSAL,
                         RoomTypeEnum.TRIPLE_THREE_BEDS, RoomTypeEnum.TRIPLE_UNIVERSAL, RoomTypeEnum.QUAD,
                         RoomTypeEnum.SINGLE_BIG_BED, RoomTypeEnum.DOUBLE_BIG_BED, RoomTypeEnum.TRIPLE_BIG_BED)

        if desired_room_type == AccommodationTypeEnum.SINGLE_BIG_BED:
            ordered_types = (RoomTypeEnum.SINGLE_BIG_BED, RoomTypeEnum.DOUBLE_BIG_BED, RoomTypeEnum.TRIPLE_BIG_BED,
                             RoomTypeEnum.QUAD, RoomTypeEnum.DOUBLE_UNIVERSAL, RoomTypeEnum.TRIPLE_UNIVERSAL,
                             RoomTypeEnum.SINGLE, RoomTypeEnum.DOUBLE_TWIN_BEDS, RoomTypeEnum.TRIPLE_THREE_BEDS)

        if desired_room_type == AccommodationTypeEnum.DOUBLE_BIG_BED:
            ordered_types = (RoomTypeEnum.DOUBLE_BIG_BED, RoomTypeEnum.DOUBLE_UNIVERSAL, RoomTypeEnum.TRIPLE_BIG_BED,
                             RoomTypeEnum.TRIPLE_UNIVERSAL, RoomTypeEnum.QUAD, RoomTypeEnum.SINGLE_BIG_BED,
                             RoomTypeEnum.DOUBLE_TWIN_BEDS, RoomTypeEnum.TRIPLE_THREE_BEDS, RoomTypeEnum.SINGLE)

        if desired_room_type == AccommodationTypeEnum.DOUBLE_TWIN_BEDS:
            ordered_types = (RoomTypeEnum.DOUBLE_TWIN_BEDS, RoomTypeEnum.DOUBLE_UNIVERSAL,
                             RoomTypeEnum.TRIPLE_THREE_BEDS, RoomTypeEnum.TRIPLE_BIG_BED, RoomTypeEnum.TRIPLE_UNIVERSAL,
                             RoomTypeEnum.QUAD,
                             RoomTypeEnum.DOUBLE_BIG_BED, RoomTypeEnum.SINGLE, RoomTypeEnum.SINGLE_BIG_BED)

        if desired_room_type == AccommodationTypeEnum.TRIPLE_THREE_BEDS:
            ordered_types = (RoomTypeEnum.DOUBLE_TWIN_BEDS, RoomTypeEnum.DOUBLE_UNIVERSAL,
                             RoomTypeEnum.TRIPLE_THREE_BEDS, RoomTypeEnum.TRIPLE_UNIVERSAL, RoomTypeEnum.QUAD,
                             RoomTypeEnum.DOUBLE_BIG_BED, RoomTypeEnum.TRIPLE_BIG_BED,
                             RoomTypeEnum.SINGLE, RoomTypeEnum.SINGLE_BIG_BED)

        return ordered_types.index(room1.room_type) <= ordered_types.index(room2.room_type)
