from decimal import Decimal

from django.db.models import OuterRef, Sum, F, Subquery, Case, When, Count, DurationField, Prefetch, DecimalField, Q
from django.db.models.functions import Coalesce, Cast

from main.business_logic.statistics.trip_utils import annotate_company_tourists_count, \
    annotate_tourists_count, annotate_route_name
from main.models.hotels.hotel_pre_booking import HotelPreBooking
from main.models.services.service_price import ServicePrice
from main.models.trips.accommodation.trip_hotel_visit import TripHotelVisit
from main.models.trips.accommodation.trip_roommates_group import TripRoommatesGroup
from main.models.trips.accommodation.trip_worker_roommates_group import TripWorkerRoommatesGroup
from main.models.trips.schedule.trip_and_service import TripAndService
from main.models.trips.tourists.client_contract.client_contract import ClientContract
from main.models.trips.tourists.trip_company import TripCompany
from main.models.trips.trip import Trip
from main.utils.queryset_utils import aggregate_subquery, extract_days_universal
from main.utils.season_date import SeasonDate


def annotate_contracts_stat(trips_queryset):
    # Все аггрегации сделаны подзапросами, чтобы обойти известный баг с JOIN-ами
    # (см. https://code.djangoproject.com/ticket/10060). Также подзапросы выполняются быстрее.

    price_subquery = aggregate_subquery(
        annotate_companies_contract_price(TripCompany.objects.filter(trip=OuterRef('pk'))),
        aggregate_fun=Sum('contract_price_q'),
        aggregate_by='trip',
    )
    tourists_count_subquery = aggregate_subquery(
        annotate_company_tourists_count(
            TripCompany.objects.filter(trip=OuterRef('pk')).filter(client_contract__isnull=False)
        ),
        aggregate_fun=Sum(Coalesce('contract_tourists_count_q', 'expected_tourists_count_q')),
        aggregate_by='trip',
    )
    commission_subquery = aggregate_subquery(
        annotate_companies_contract_stat(TripCompany.objects.filter(trip=OuterRef('pk'))),
        aggregate_fun=Sum('commission_q'),
        aggregate_by='trip',
    )
    return trips_queryset.annotate(
        contracts_price_q=Coalesce(Subquery(price_subquery), Decimal(0)),
        contract_tourists_count_q=Coalesce(Subquery(tourists_count_subquery), 0),
        contracts_commission_q=Coalesce(Subquery(commission_subquery), Decimal(0)),
    )


def annotate_companies_contract_price(companies_queryset):
    services_price_subquery = aggregate_subquery(
        ClientContract.objects.filter(trip_company=OuterRef('pk')),
        aggregate_fun=Sum(Case(
            When(
                clientcontractandservice__price_type=1,
                then=F('clientcontractandservice__cost') * F('clientcontractandservice__tourist_count'),
            ),
            default=F('clientcontractandservice__cost'),
        )),
        aggregate_by='trip_company',
    )
    return companies_queryset.annotate(
        price_without_services_q=Coalesce(
            F('client_contract__base_price') - F('client_contract__discount'),
            Decimal(0),
        ),
        services_price_q=Coalesce(Subquery(services_price_subquery), Decimal(0)),
        contract_price_q=F('services_price_q') + F('price_without_services_q'),
    )


def annotate_companies_contract_stat(companies_queryset):
    real_prepayment_subquery = aggregate_subquery(
        companies_queryset.filter(pk=OuterRef('pk')),
        aggregate_fun=Coalesce(
            Sum(
                'client_contract__payment_expense_items__payment__amount',
                filter=Q(
                    is_draft=True,
                    client_contract__payment_expense_items__payment__is_outgoing=False,
                )
            ),
            Decimal(0)
        ),
        aggregate_by='pk',
    )
    return annotate_companies_contract_price(annotate_company_tourists_count(companies_queryset)).annotate(
        commission_q=Case(
            When(supplier__isnull=True, then=0),
            When(client_contract__isnull=True, then=0),
            When(commission_type=1, then='supplier_commission'),
            When(commission_type=2, then=F('contract_price_q') * F('supplier_commission') / 100),
            default=0,
            output_field=DecimalField(),
        ),
        commission_paid_q=Coalesce(Sum('commission_expense_items__payment__amount'), Decimal(0)),
        commission_remaining_q=F('commission_q') - F('commission_paid_q'),
        real_prepayment_q=Coalesce(Subquery(real_prepayment_subquery), Decimal(0)),
    )


def get_contracts_price_raw_query(trips):
    """
    Этот SQL-запрос написан Рустемом для замены неэффективного подсчёта средствами Джанго и питона
    (в цикле пробегались туры, договоры и услуги; при этом для каждого тура выполнялось несколько запросов к БД).
    Однако после этого удалось сделать более эффективный (и, вроде как, не очень страшный) запрос на Джанго
    (см. функцию выше; она выполняет всего одно обращение к БД из Джанго на всю пачку туров).
    Данный запрос оставлен здесь для примера, как в Джанго можно вставлять запросы на чистом SQL.
    """
    pk_list = [x.pk for x in trips]
    args_placeholder = ", ".join("%s" for _ in pk_list)
    return Trip.objects.raw(
        f"""
        SELECT sum(main_clientcontract.base_price - main_clientcontract.discount +
            (SELECT coalesce(sum(
                case 
                    when price_type == 1 then cost * tourist_count
                    else cost
                end
            ), 0)
            FROM main_clientcontractandservice
            WHERE main_clientcontract.id = main_clientcontractandservice.contract_id)) AS contracts_price_q,
            main_trip.id, main_trip.name, main_trip.start_date, main_trip.route_id 
        FROM main_clientcontract
        INNER JOIN main_tripcompany on main_clientcontract.trip_company_id = main_tripcompany.id
        INNER JOIN main_trip on main_tripcompany.trip_id = main_trip.id
        WHERE trip_company_id in (SELECT id FROM main_tripcompany WHERE trip_id in ({args_placeholder}))
        GROUP by main_trip.start_date
        ORDER by main_trip.start_date
        """,
        pk_list,
    )


def calc_contracts_price_raw_query_for_trip(trip):
    qs = Trip.objects.filter(pk=trip.pk)
    qs = get_contracts_price_raw_query(qs)
    return sum(x.contracts_price_q for x in qs)


def annotate_hotels_stat(trips_queryset):
    def get_hotel_visit_night_price_subquery(model_class):
        roommates_count_subquery = aggregate_subquery(
            model_class.objects.filter(pk=OuterRef('pk')),
            aggregate_fun=Count('roommates'),
            aggregate_by='pk',
        )
        return aggregate_subquery(
            model_class.objects.
                filter(trip_hotel_visit=OuterRef('pk')).
                filter(room_reservation__isnull=False).
                annotate(
                    price_q=F('room_reservation__hotel_pre_booking_and_room__room_type__price'),
                    price_single_q=Coalesce(
                        F('room_reservation__hotel_pre_booking_and_room__room_type__price_single'),
                        'price_q',
                    ),
                    roommates_count_q=Subquery(roommates_count_subquery),
                ),
            aggregate_fun=Sum(Case(
                When(
                    roommates_count_q=1,
                    then=F('price_single_q'),
                ),
                default=F('price_q'),
            )),
            aggregate_by='trip_hotel_visit',
        )

    workers_count_subquery = aggregate_subquery(
        Trip.objects.filter(pk=OuterRef('pk')),
        aggregate_fun=Count('workers'),
        aggregate_by='pk',
    )

    tourists_with_room_count_subquery = aggregate_subquery(
        TripRoommatesGroup.objects.filter(trip_hotel_visit=OuterRef('pk')).filter(room_reservation__isnull=False),
        aggregate_fun=Count('roommates'),
        aggregate_by='trip_hotel_visit',
    )

    workers_with_room_count_subquery = aggregate_subquery(
        TripWorkerRoommatesGroup.objects.filter(trip_hotel_visit=OuterRef('pk')).filter(room_reservation__isnull=False),
        aggregate_fun=Count('roommates'),
        aggregate_by='trip_hotel_visit',
    )

    return trips_queryset.prefetch_related(
        Prefetch(
            'trip_hotel_visits',
            queryset=TripHotelVisit.objects.all().prefetch_related(
                Prefetch(
                    'pre_bookings',
                    queryset=HotelPreBooking.objects.all().annotate(
                        rooms_price_per_night_sum_q=Coalesce(Sum(
                            Coalesce(F('hotelprebookingandroom__room_type__price'), Decimal(0)) *
                            F('hotelprebookingandroom__count')
                        ), Decimal(0)),
                        rooms_capacity_sum_q=Coalesce(Sum(
                            F('hotelprebookingandroom__room_type__max_adults_count') *
                            F('hotelprebookingandroom__count')
                        ), 0),
                    ),
                    to_attr='pre_booking_list_q'
                ),
            ).annotate(
                tourists_with_room_count_q=Coalesce(Subquery(tourists_with_room_count_subquery), 0),
                workers_with_room_count_q=Coalesce(Subquery(workers_with_room_count_subquery), 0),
                persons_with_room_count_q=F('tourists_with_room_count_q') + F('workers_with_room_count_q'),
            ).annotate(
                night_price_q=Coalesce(Subquery(get_hotel_visit_night_price_subquery(TripRoommatesGroup)), Decimal(0)) +
                    Coalesce(Subquery(get_hotel_visit_night_price_subquery(TripWorkerRoommatesGroup)), Decimal(0)),
                duration_nights_q=extract_days_universal(
                    Cast(F('end_date') - F('start_date'), output_field=DurationField())
                ),
                total_price_q=F('night_price_q') * F('duration_nights_q'),
            ),
            to_attr='trip_hotel_visits_list_q',
        ),
    ).annotate(
        workers_count_q=Coalesce(Subquery(workers_count_subquery), 0),
    )


def annotate_services_stat(trips_queryset):
    # TODO: сделать подзапросы, как для договоров (тут есть проблема, как в запросе узнать цену в конкретный день тура)
    return trips_queryset.prefetch_related(
        Prefetch(
            'tripandservice_set',
            queryset=TripAndService.objects.all().select_related('service').prefetch_related(
                Prefetch(
                    'service__prices',
                    queryset=ServicePrice.objects.all(),
                    to_attr='prices_list_q'
                )
            ),
            to_attr='tripandservice_list_q'
        ),
    )


def annotate_money_stat(trips_queryset):
    return annotate_route_name(
        annotate_tourists_count(
            annotate_services_stat(
                annotate_hotels_stat(
                    annotate_contracts_stat(trips_queryset)
                )
            )
        )
    )


def calc_services_price_for_trip_with_stat(trip, tourists_count):
    total_price = Decimal(0)
    for trip_and_service in trip.tripandservice_list_q:
        service = trip_and_service.service
        date = SeasonDate.from_date(trip_and_service.date)
        relevant_prices = [x for x in service.prices_list_q if x.start_date <= date <= x.end_date]
        if len(relevant_prices) > 0:
            total_price += relevant_prices[0].get_price(person_count=max(tourists_count, service.min_group_size))
    return total_price


def calc_hotels_price_for_trip_with_stat(trip):
    # TODO: как посчитать сумму цен в самом запросе (проблема в том, что статистика по заездам формируется в prefetch)?
    return sum([x.total_price_q for x in trip.trip_hotel_visits_list_q], Decimal(0))


def calc_persons_with_rooms_for_trip_with_stat(trip):
    return sum([x.persons_with_room_count_q for x in trip.trip_hotel_visits_list_q], 0)


def calc_rooms_capacity_for_trip_with_stat(trip):
    capacity = 0
    for hotel_visit in trip.trip_hotel_visits_list_q:
        for booking in hotel_visit.pre_booking_list_q:
            capacity += booking.rooms_capacity_sum_q
    return capacity


def calc_avg_booking_price_per_person(hotel_visit_with_stat):
    nights_count = hotel_visit_with_stat.duration_nights
    total_rooms_capacity = 0
    total_rooms_price = Decimal(0)
    for booking in hotel_visit_with_stat.pre_booking_list_q:
        total_rooms_price += booking.rooms_price_per_night_sum_q * nights_count
        total_rooms_capacity += booking.rooms_capacity_sum_q
    if total_rooms_capacity > 0:
        price_per_person = total_rooms_price / total_rooms_capacity
    else:
        price_per_person = Decimal(0)
    return price_per_person
