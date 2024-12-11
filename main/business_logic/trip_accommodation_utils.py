from operator import methodcaller

from django.db import transaction
from django.template.defaultfilters import pluralize

import main.models.trips.tourists.trip_company
from main.models.clients.client import Client
from main.models.trips.schedule.abstract_trip_and_city import AbstractTripAndCity
from main.models.trips.accommodation.abstract_trip_roommates_group import AbstractTripRoommatesGroup
from main.models.trips.accommodation.trip_room_reservation import TripRoomReservation
from main.models.trips.accommodation.trip_roommates_group import TripRoommatesGroup
from main.models.trips.accommodation.trip_worker_room_reservation import TripWorkerRoomReservation
from main.models.trips.accommodation.trip_worker_roommates_group import TripWorkerRoommatesGroup
from main.models.workers.trip_worker import TripWorker
from main.templatetags.pluralize_ru import pluralize_ru
from main.utils.utils import get_unique_name

AccommodationTypeEnum = main.models.trips.tourists.trip_company.TripCompany.AccommodationTypeEnum


def make_roommate_pairs(persons, hotel_visit, group_class):
    """Объединяет гостей (или работников) в группы попарно. Возвращает список созданных групп."""
    persons = sorted(persons, key=methodcaller('age'))
    groups = []
    start_ind = 0
    if len(persons) > 1 and len(persons) % 2 != 0 and \
            persons[1].age() - persons[0].age() > persons[-1].age() - persons[-2].age():
        # Если число гостей нечётное и разница в возрасте между самыми молодыми гостями больше
        # разницы в возрасте между самыми старшими, то самого молодого гостя оставляем без пары.
        start_ind = 1
    for i in range(start_ind, len(persons), 2):
        if i + 1 >= len(persons):
            break
        groups.append(create_roommates_group(hotel_visit, [persons[i], persons[i + 1]], group_class))
    return groups


def cleanup_hotel_visit(hotel_visit):
    delete_empty_roommate_groups(hotel_visit)
    create_roommate_groups_for_all_trip_companies_and_workers(hotel_visit)


def delete_empty_roommate_groups(hotel_visit):
    """Удаляем пустые группы соседей (такое может быть, если вручную удалять клиентов из админки)."""
    for group in hotel_visit.all_roommate_groups():
        if not group.roommates.exists():
            group.delete()


def create_roommate_groups_for_all_trip_companies_and_workers(hotel_visit):
    """Создаёт группы соседей для всех компаний туристов и работников (если они ещё не были созданы)."""
    create_roommate_groups_for_all_trip_companies(hotel_visit)
    create_roommate_groups_for_all_trip_workers(hotel_visit)


def create_roommate_groups_for_all_trip_companies(hotel_visit):
    """Создаёт группы соседей, по возможности совпадающие с компаниями туристов
    (если группы соседей ещё не были созданы).
    """
    trip = hotel_visit.trip
    for company in trip.trip_companies.all():
        related_roommates_group = company.get_single_related_roommate_group(hotel_visit)
        tourists_without_roommates = []
        for tourist in company.tourists.all():
            roommates_group = tourist.get_roommates_group(hotel_visit)
            if not roommates_group:
                # Если другие туристы из компании уже добавлены в группу соседей,
                # но номер для них ещё не забронирован, то добавляем туриста в ту же группу
                if related_roommates_group and not related_roommates_group.try_get_room_reservation():
                    related_roommates_group.roommates.add(tourist)
                else:
                    tourists_without_roommates.append(tourist)
        if tourists_without_roommates:
            create_roommates_group(hotel_visit, tourists_without_roommates, TripRoommatesGroup)


def create_roommate_groups_for_all_trip_workers(hotel_visit):
    """Создаёт группы соседей для всех работников - гидов и водителей (если они ещё не были созданы)."""
    from main.business_logic.trip_auto_accommodation_helper import TripAutoAccommodationHelper
    trip = hotel_visit.trip
    for worker in trip.workers.all():
        if not worker.get_roommates_group(hotel_visit):
            create_roommates_group(hotel_visit, [worker], TripWorkerRoommatesGroup)
    helper = TripAutoAccommodationHelper(hotel_visit)
    helper.optimize_workers_accommodation()


def default_roommates_group_name(main_person):
    return f"{main_person.surname} и Ко"


def create_roommates_group(hotel_visit, persons, group_class):
    """Создаёт новую группу соседей с указанными туристами или работниками, при этом удаляет их из прежних групп."""
    for person in persons:
        old_group = person.get_roommates_group(hotel_visit)
        if old_group:
            AbstractTripRoommatesGroup.remove_from_roommates_group(person, old_group)
    existing_groups = hotel_visit.tourist_roommate_groups.all() if group_class == TripRoommatesGroup \
        else hotel_visit.worker_roommate_groups.all()
    group = group_class(
        trip_hotel_visit=hotel_visit,
        name=get_unique_name(default_roommates_group_name(persons[0]), set([x.name for x in existing_groups])),
    )
    group.save()
    group.roommates.add(*persons)
    return group


def may_change_roommates(person, hotel_visit):
    group = person.get_roommates_group(hotel_visit)
    return not group or group.may_change_roommates()


# TODO: аналог функции trip_company_update_members, надо бы их обобщить
def roommates_group_update_members(group, is_tourists_group, new_person_pks):
    """
    Изменяет состав группы соседей по номеру.
    Возвращает пару - флаг успех/неудача и список ошибок.
    """
    member_class = Client if is_tourists_group else TripWorker
    old_persons = set(group.roommates.all())
    new_persons = set(member_class.objects.filter(pk__in=new_person_pks))
    deleted_persons = old_persons - new_persons
    added_persons = new_persons - old_persons
    if not added_persons and not deleted_persons:
        return True, []
    if not group.may_change_roommates():
        return False, ["Ошибка: для этой группы уже выбран номер в гостинице."]
    if len(deleted_persons) == len(old_persons):
        return False, ["Ошибка: нельзя удалить всех из группы соседей."]
    for person in new_persons:
        if not may_change_roommates(person, group.trip_hotel_visit):
            return False, [f"Ошибка: гость {person.full_name()} входит в группу соседей "
                           f"с уже выбранным номером в гостинице."]

    with transaction.atomic():
        for added_person in added_persons:
            old_group = added_person.get_roommates_group(group.trip_hotel_visit)
            # Удаляем туриста/работника из прежней группы в этом туре
            if old_group:
                AbstractTripRoommatesGroup.remove_from_roommates_group(added_person, old_group)
            # Добавляем туриста/работника в новую группу
            group.roommates.add(added_person)
        for deleted_person in deleted_persons:
            group.roommates.remove(deleted_person)
            create_roommates_group(group.trip_hotel_visit, [deleted_person], type(group))

        if not group.roommates.exists():
            group.delete()

    return True, []


def reserve_room(roommates_group, pre_booking, room_type):
    """Производит резервирование номера для указанной группы соседей.
    Если номер доступен, возвращает резерв, в противном случае возвращает None.
    """
    hotel_visit = roommates_group.trip_hotel_visit
    booking_and_room = pre_booking.hotelprebookingandroom_set.filter(room_type=room_type).first()
    if booking_and_room and booking_and_room.may_reserve_next_room(hotel_visit):
        room_number = hotel_visit.get_next_room_number(room_type)
        is_tourists_group = isinstance(roommates_group, TripRoommatesGroup)
        reservation_class = TripRoomReservation if is_tourists_group else TripWorkerRoomReservation
        reservation = reservation_class(
            roommates_group=roommates_group,
            hotel_pre_booking_and_room=booking_and_room,
            room_number=room_number,
        )
        reservation.save()
        return reservation
    return None


def get_accommodation_tab_name(hotel_visit, city):
    trip = hotel_visit.trip
    start_date = hotel_visit.start_date
    end_date = hotel_visit.end_date
    nights_count = (end_date - start_date).days
    parts = [pluralize(nights_count, "День,Дни "), str(trip.get_day_number(start_date))]
    if nights_count > 1:
        parts.extend(["-", str(trip.get_day_number(end_date) - 1)])
    nights_str = pluralize_ru(nights_count, "ночь,ночи,ночей")
    parts.extend([f" · {nights_count} {nights_str}"])
    parts.extend(["\n", "Заезд ", start_date.strftime("%d.%m"), " · Выезд ", end_date.strftime("%d.%m")])
    parts.extend(["\n", city.name if city else 'Город не выбран'])
    return ''.join(parts)


def get_accommodation_tabs(trip):
    """Возвращает список атрибутов для вкладок, на каждый заезд - одна вкладка."""
    tabs = []
    day = 1
    while day < trip.duration_days:
        city = trip.get_city(day_number=day, objective=AbstractTripAndCity.ObjectiveEnum.OVERNIGHT)
        hotel_visit = trip.get_hotel_visit(day)
        if not hotel_visit:
            hotel_visit = trip.new_hotel_visit(day)
        tabs.append({
            'day': day,
            'text': get_accommodation_tab_name(hotel_visit, city),
            'hotel_visit': hotel_visit,
            'item_id': hotel_visit.get_active_sidebar_item(),
        })
        day = trip.get_day_number(hotel_visit.end_date)
    return tabs
