from django.db import transaction

import main.models.trips.tourists.abstract_trip_transfer
import main.models.trips.tourists.trip_company
from main.models.clients.client import Client
from main.models.trips.tourists.trip_company import TripCompany

AccommodationTypeEnum = main.models.trips.tourists.trip_company.TripCompany.AccommodationTypeEnum
TransferTypeEnum = main.models.trips.tourists.abstract_trip_transfer.AbstractTripTransfer.TransferTypeEnum


def create_dummy_companies_if_needed(trip):
    """Создаём компании для тех туристов, которые ещё без компании."""
    for tourist in trip.tourists.all():
        if not tourist.get_trip_company(trip):
            trip.add_tourist_to_dummy_company(tourist)


def may_change_company(tourist, trip):
    company = tourist.get_trip_company(trip)
    return not company or company.may_change_tourists()


def trip_company_update_members(company, client_pks):
    """
    Изменяет состав компании гостей.
    Возвращает пару - флаг успех/неудача и список ошибок (а в случае успеха - ворнингов).
    """
    # TODO: добавить тесты
    def transfer_to_str(transfer):
        if not transfer:
            return "-"
        return f"{transfer.get_transfer_type_display()} {transfer.date_time_local.strftime('%d.%m.%y %H:%M')}"

    trip = company.trip
    old_tourists = set(company.tourists.all())
    new_tourists = set(Client.objects.filter(pk__in=client_pks))
    deleted_tourists = old_tourists - new_tourists
    added_tourists = new_tourists - old_tourists
    warnings = []

    if not added_tourists and not deleted_tourists:
        return True, []
    if not company.may_change_tourists():
        return False, ["Ошибка: с этой компанией уже оформлен договор или выбран тип размещения"]
    if len(deleted_tourists) == len(old_tourists):
        return False, ["Ошибка: нельзя удалить из компании всех гостей"]
    for tourist in [*added_tourists, *deleted_tourists]:
        if not may_change_company(tourist, trip):
            return False, [f"Ошибка: гость {tourist.signature_initials()} входит в компанию "
                           f"с уже оформленным договором или выбранным типом размещения"]

    with transaction.atomic():
        changed_companies = set()
        for added_tourist in added_tourists:
            old_company = added_tourist.get_trip_company(trip)

            # Удаляем клиента из прежней компании в этом туре
            if old_company:
                # Предварительно исключаем компанию из set-а, т.к. после удаления компании мы уже не сможем этого сделать
                changed_companies.discard(old_company)
                TripCompany.remove_from_company(added_tourist, old_company)
                if old_company.pk:
                    # Если компания не была удалена, добавляем её в коллекцию
                    changed_companies.add(old_company)

            # Копируем трансферы из новой компании
            for old_transfer, new_transfer in [
                (added_tourist.arrival(trip), company.arrival()),
                (added_tourist.departure(trip), company.departure())
            ]:
                if old_transfer or new_transfer:
                    warnings.append(f"Гость {tourist.signature_initials()}. "
                                    f"""Прежние данные о трансфере: "{transfer_to_str(old_transfer)}", """ 
                                    f"""новые данные: "{transfer_to_str(new_transfer)}" """)
                    if old_transfer:
                        old_transfer.delete()
                    if new_transfer:
                        added_tourist.copy_transfer_from(new_transfer.pk)

            # Добавляем туриста в новую компанию
            company.tourists.add(added_tourist)
        for deleted_tourist in deleted_tourists:
            company.tourists.remove(deleted_tourist)
            trip.add_tourist_to_dummy_company(deleted_tourist)

        if not company.tourists.exists():
            company.delete()
        elif added_tourists or deleted_tourists:
            changed_companies.add(company)

        for x in changed_companies:
            on_company_tourists_change(x)

    return True, warnings


def on_company_tourists_change(company):
    # Переименовываем компанию, если надо
    if all(x.surname not in company.name for x in company.tourists.all()):
        company.name = TripCompany.default_company_name(company.tourists.first(), company.trip.trip_companies.all())
    company.desired_room_type = AccommodationTypeEnum.NONE
    company.save()


def delete_empty_trip_companies(trip):
    """Удаляет пустые компании клиентов (такое может быть, если вручную удалять клиентов из админки)."""
    for company in trip.trip_companies.all():
        if not company.tourists.exists():
            company.delete()


def cleanup_trip_companies(trip):
    delete_empty_trip_companies(trip)
    create_dummy_companies_if_needed(trip)
