from django import forms
from django.contrib import admin, auth
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _

from main.models.agency.agency import Agency
from main.models.agency.agency_employee import AgencyEmployee
from main.models.agency.agency_employee_avatar import AgencyEmployeeAvatar
from main.models.agency.agency_social_network_contact import AgencySocialNetworkContact
from main.models.clients.client import Client
from main.models.clients.client_adat_extra_info import ClientAdatExtraInfo
from main.models.clients.coupons.coupon import Coupon
from main.models.clients.coupons.coupon_expiration_rule import CouponExpirationRule
from main.models.clients.coupons.coupon_label import CouponLabel
from main.models.clients.coupons.coupon_max_uses_rule import CouponMaxUsesRule
from main.models.clients.coupons.coupon_rule import CouponRule
from main.models.clients.coupons.coupon_usage_as_referral import CouponUsageAsReferral
from main.models.clients.coupons.coupon_usage_in_trip import CouponUsageInTrip
from main.models.clients.coupons.discount import Discount
from main.models.clients.guest_form.guest_form_link import GuestFormLink
from main.models.clients.guest_form.inbox_client_data import InboxClientData
from main.models.clients.guest_form.inbox_identity_document import InboxIdentityDocument
from main.models.clients.guest_form.inbox_phone_contact import InboxPhoneContact
from main.models.clients.guest_form.inbox_registration_data import InboxRegistrationData
from main.models.clients.person import Person
from main.models.clients.person_address import PersonAddress
from main.models.clients.person_email_contact import PersonEmailContact
from main.models.clients.person_identity_document import PersonIdentityDocument
from main.models.clients.person_phone_contact import PersonPhoneContact
from main.models.clients.person_registration_data import PersonRegistrationData
from main.models.clients.person_social_network_contact import PersonSocialNetworkContact
from main.models.demo.demo_request import DemoRequest, DemoRequestAdmin
from main.models.directory.city import City
from main.models.directory.restaurant import Restaurant
from main.models.hotels.hotel import Hotel
from main.models.hotels.hotel_pre_booking import HotelPreBooking
from main.models.hotels.hotel_pre_booking_and_room import HotelPreBookingAndRoom
from main.models.hotels.hotel_room_type import HotelRoomType
from main.models.money.agency_payment_party import AgencyPaymentParty
from main.models.money.agency_payment_token import AgencyPaymentToken
from main.models.money.bank_details import BankDetails
from main.models.money.base_payment_party import BasePaymentParty
from main.models.money.base_money_account import BaseMoneyAccount
from main.models.money.bank_money_account import BankMoneyAccount
from main.models.money.cash_money_account import CashMoneyAccount
from main.models.money.client_contract_expense_item import ClientContractExpenseItem
from main.models.money.client_contract_service_expense_item import ClientContractServiceExpenseItem
from main.models.money.draft_contract_payment import DraftContractPayment
from main.models.money.guide_extra_expense_item import GuideExtraExpenseItem
from main.models.money.hotel_expense_item import HotelExpenseItem
from main.models.money.payment import Payment
from main.models.money.payment_media import PaymentMedia
from main.models.money.person_payment_party import PersonPaymentParty
from main.models.money.supplier_commission_expense_item import SupplierCommissionExpenseItem
from main.models.money.supplier_payment_party import SupplierPaymentParty
from main.models.money.trip_service_expense_item import TripServiceExpenseItem
from main.models.routes.route import Route
from main.models.routes.route_and_city import RouteAndCity
from main.models.routes.route_and_food import RouteAndFood
from main.models.routes.route_and_service import RouteAndService
from main.models.routes.route_day import RouteDay
from main.models.services.guest_cabinet_link import GuestCabinetLink
from main.models.services.legal_supplier import LegalSupplier
from main.models.services.legal_supplier_social_network_contact import LegalSupplierSocialNetworkContact
from main.models.services.person_supplier import PersonSupplier
from main.models.services.service import Service
from main.models.services.service_label import ServiceLabel
from main.models.services.service_media import ServiceMedia
from main.models.services.service_price import ServicePrice
from main.models.services.supplier import Supplier
from main.models.services.supplier_cabinet_link import SupplierCabinetLink
from main.models.trips.departure_point import DeparturePoint
from main.models.trips.tourists.client_contract.client_contract import ClientContract
from main.models.trips.tourists.client_contract.client_contract_and_service import ClientContractAndService
from main.models.trips.inbox_trip_company import InboxTripCompany
from main.models.trips.meal_order import MealOrder
from main.models.trips.trip import Trip
from main.models.trips.tourists.trip_airplane_transfer import TripAirplaneTransfer
from main.models.trips.schedule.trip_and_city import TripAndCity
from main.models.trips.tourists.trip_and_client import TripAndClient
from main.models.trips.schedule.trip_and_service import TripAndService
from main.models.trips.trip_and_trip_worker import TripAndTripWorker
from main.models.trips.tourists.trip_company import TripCompany
from main.models.trips.schedule.trip_day import TripDay
from main.models.trips.accommodation.trip_hotel_visit import TripHotelVisit
from main.models.trips.trip_media import TripMedia
from main.models.trips.trip_restaurant_visit import TripRestaurantVisit
from main.models.trips.accommodation.trip_room_reservation import TripRoomReservation
from main.models.trips.accommodation.trip_roommates_group import TripRoommatesGroup
from main.models.trips.accommodation.trip_worker_room_reservation import TripWorkerRoomReservation
from main.models.trips.accommodation.trip_worker_roommates_group import TripWorkerRoommatesGroup
from main.models.workers.driver_info import DriverInfo
from main.models.workers.guide_cabinet_link import GuideCabinetLink
from main.models.workers.trip_worker import TripWorker


# Дескриптор для добавления полей модели AgencyEmployee в админские формы создания/редактирования пользователей
class AgencyEmployeeInline(admin.StackedInline):
    model = AgencyEmployee
    can_delete = False


# Новый UserAdmin
class CustomUserAdmin(UserAdmin):
    inlines = (AgencyEmployeeInline,)
    # Прячем поля для редактирования персональных данных, т.к. у нас для этого и есть AgencyEmployee
    fieldsets = [x for x in UserAdmin.fieldsets if x[0] != _('Personal info')]


class AgencyPaymentTokenForm(forms.ModelForm):
    secret_key = forms.CharField(
        label="Секретный ключ",
        strip=False,
        widget=forms.PasswordInput(),
    )

    class Meta:
        model = AgencyPaymentToken
        fields = ['agency', 'payment_system', 'account_id', 'secret_key']


class AgencyPaymentTokenAdmin(admin.ModelAdmin):
    form = AgencyPaymentTokenForm


# Перерегистрируем UserAdmin-а
admin.site.unregister(auth.get_user_model())
admin.site.register(auth.get_user_model(), CustomUserAdmin)


admin.site.register(Agency)
admin.site.register(City)
admin.site.register(Person)
admin.site.register(Client)
admin.site.register(InboxClientData)
admin.site.register(TripWorker)
admin.site.register(DriverInfo)
admin.site.register(AgencyEmployee)
admin.site.register(AgencyEmployeeAvatar)
admin.site.register(PersonIdentityDocument)
admin.site.register(InboxIdentityDocument)
admin.site.register(PersonRegistrationData)
admin.site.register(InboxRegistrationData)
admin.site.register(InboxPhoneContact)
admin.site.register(PersonAddress)
admin.site.register(PersonPhoneContact)
admin.site.register(PersonEmailContact)
admin.site.register(PersonSocialNetworkContact)
admin.site.register(ClientAdatExtraInfo)
admin.site.register(Coupon)
admin.site.register(CouponLabel)
admin.site.register(CouponRule)
admin.site.register(CouponMaxUsesRule)
admin.site.register(CouponExpirationRule)
admin.site.register(CouponUsageInTrip)
admin.site.register(CouponUsageAsReferral)
admin.site.register(Discount)
admin.site.register(Hotel)
admin.site.register(HotelRoomType)
admin.site.register(HotelPreBooking)
admin.site.register(HotelPreBookingAndRoom)
admin.site.register(Restaurant)
admin.site.register(Route)
admin.site.register(RouteDay)
admin.site.register(RouteAndCity)
admin.site.register(RouteAndFood)
admin.site.register(Trip)
admin.site.register(TripDay)
admin.site.register(TripAndCity)
admin.site.register(TripAndClient)
admin.site.register(TripAndTripWorker)
admin.site.register(TripCompany)
admin.site.register(InboxTripCompany)
admin.site.register(ClientContract)
admin.site.register(TripAirplaneTransfer)
admin.site.register(TripHotelVisit)
admin.site.register(TripRoomReservation)
admin.site.register(TripWorkerRoomReservation)
admin.site.register(TripRoommatesGroup)
admin.site.register(TripWorkerRoommatesGroup)
admin.site.register(TripRestaurantVisit)
admin.site.register(MealOrder)
admin.site.register(TripMedia)
admin.site.register(Service)
admin.site.register(ServiceLabel)
admin.site.register(ServicePrice)
admin.site.register(TripAndService)
admin.site.register(RouteAndService)
admin.site.register(ClientContractAndService)
admin.site.register(Supplier)
admin.site.register(PersonSupplier)
admin.site.register(LegalSupplier)
admin.site.register(LegalSupplierSocialNetworkContact)
admin.site.register(ServiceMedia)
admin.site.register(GuideCabinetLink)
admin.site.register(Payment)
admin.site.register(ClientContractExpenseItem)
admin.site.register(HotelExpenseItem)
admin.site.register(TripServiceExpenseItem)
admin.site.register(ClientContractServiceExpenseItem)
admin.site.register(GuideExtraExpenseItem)
admin.site.register(SupplierCommissionExpenseItem)
admin.site.register(BasePaymentParty)
admin.site.register(PersonPaymentParty)
admin.site.register(SupplierPaymentParty)
admin.site.register(AgencyPaymentParty)
admin.site.register(PaymentMedia)
admin.site.register(DemoRequest, DemoRequestAdmin)
admin.site.register(BaseMoneyAccount)
admin.site.register(CashMoneyAccount)
admin.site.register(BankMoneyAccount)
admin.site.register(BankDetails)
admin.site.register(GuestFormLink)
admin.site.register(SupplierCabinetLink)
admin.site.register(GuestCabinetLink)
admin.site.register(AgencyPaymentToken, AgencyPaymentTokenAdmin)
admin.site.register(DraftContractPayment)
admin.site.register(AgencySocialNetworkContact)
admin.site.register(DeparturePoint)
