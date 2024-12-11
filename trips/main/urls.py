from django.urls import path

from main.views.supplier_cabinet.add_prev_tourist_view import AddPrevTouristView
from .models.routes.route import Route
from .models.workers.trip_worker import TripWorker
from .utils.home_folder import HomeFolder
from .views.guest_cabinet.add_tourist_view import AddTouristView as GuestCabinetAddTouristView
from .views.guest_cabinet.dashboard_view import DashboardView as GuestCabinetDashboardView
from .views.guest_cabinet.guest_cabinet_get_trip_info_view import GuestCabinetGetTripInfoView
from .views.guest_cabinet.guest_cabinet_image_serve_view import GuestCabinetImageServeView
from .views.guest_cabinet.guest_cabinet_logo_view import GuestCabinetLogoView
from .views.guest_cabinet.guest_thanks_view import GuestThanksView
from .views.guest_cabinet.yookassa_webhook_view import YookassaWebhookView
from main.views.guest_cabinet.guest_pdf_view import GuestPdfView
from .views.media.favicon_image_view import FaviconImageView
from .views.supplier_cabinet.add_tourist_view import AddTouristView as SupplierCabinetAddTouristView
from .views.supplier_cabinet.commission_details_view import CommissionDetailsView
from .views.supplier_cabinet.dashboard_view import DashboardView as SupplierCabinetDashboardView
from .views.supplier_cabinet.future_trips_list_view import FutureTripsListView
from .views.supplier_cabinet.get_trip_info_view import GetTripInfoView
from .views.supplier_cabinet.guest_cabinet_get_or_create_view import GuestCabinetGetOrCreateView
from .views.supplier_cabinet.supplier_cabinet_image_serve_view import SupplierCabinetImageServeView
from .views.supplier_cabinet.supplier_cabinet_logo_view import SupplierCabinetLogoView

urlpatterns = [
    path('supplier_lk/<str:cabinet_id>/', SupplierCabinetDashboardView.as_view(), name='supplier_lk_dashboard'),
    path('supplier_lk/<str:cabinet_id>/trips/',
         FutureTripsListView.as_view(show_excursions=False, show_trips=True),
         name='supplier_lk_multi_day_trips'),
    path('supplier_lk/<str:cabinet_id>/excursions/',
         FutureTripsListView.as_view(show_excursions=True, show_trips=False),
         name='supplier_lk_excursions'),
    path('supplier_lk/<str:cabinet_id>/commission_details/', CommissionDetailsView.as_view(),
         name='supplier_lk_commission_details'),
    path('supplier_lk/<str:cabinet_id>/trips/<int:route_pk>/add_guest/', SupplierCabinetAddTouristView.as_view(),
         name='supplier_lk_add_tourist'),
    path('supplier_lk/<str:cabinet_id>/trips/<int:route_pk>/add_prev_guest/', AddPrevTouristView.as_view(),
         name='supplier_lk_add_prev_tourist'),
    path('supplier_lk/<str:cabinet_id>/trips/<int:route_pk>/get_trip_info/', GetTripInfoView.as_view(),
         name='supplier_lk_get_trip_info'),
    path('supplier_lk/<str:cabinet_id>/create_guest_cabinet/', GuestCabinetGetOrCreateView.as_view(),
         name='supplier_lk_get_guest_link'),
    path('supplier_lk/<str:cabinet_id>/trips/<int:route_pk>/photo/',
         SupplierCabinetImageServeView.as_view(model=Route, pk_url_kwarg='route_pk'),
         name='supplier_lk_route_photo'),
    path('supplier_lk/<str:cabinet_id>/guides/<int:pk>/photo/',
         SupplierCabinetImageServeView.as_view(model=TripWorker),
         name='supplier_lk_guide_photo'),
    path('supplier_lk/<str:cabinet_id>/logo/', SupplierCabinetLogoView.as_view(), name='supplier_lk_logo'),
    path('guest/<str:cabinet_id>/', GuestCabinetDashboardView.as_view(), name='guest_lk_dashboard'),
    path('guest/<str:cabinet_id>/trips/<int:route_pk>/get_trip_info/', GuestCabinetGetTripInfoView.as_view(),
         name='guest_lk_get_trip_info'),
    path('guest/<str:cabinet_id>/trips/<int:route_pk>/add_guest/', GuestCabinetAddTouristView.as_view(),
         name='guest_lk_add_tourist'),
    path('guest/<str:cabinet_id>/thanks/<str:contract_slug>/', GuestThanksView.as_view(), name='guest_lk_thanks'),
    path('guest/<str:cabinet_id>/logo/', GuestCabinetLogoView.as_view(), name='guest_lk_logo'),
    path('guest/<str:cabinet_id>/trips/<int:route_pk>/photo/',
         GuestCabinetImageServeView.as_view(model=Route, pk_url_kwarg='route_pk'),
         name='guest_lk_route_photo'),
    path('guest/<str:cabinet_id>/guides/<int:pk>/photo/',
         GuestCabinetImageServeView.as_view(model=TripWorker),
         name='guest_lk_guide_photo'),
    path('guest_webhooks/yookassa/', YookassaWebhookView.as_view(), name='guest_yoo_webhook'),
    path('public_offer/<str:guest_cabinet_id>/',
         GuestPdfView.as_view(
             template_name=HomeFolder.public_offer_file_name,
             user_name="Публичная оферта.pdf",
             cabinet_id_url_kwarg='guest_cabinet_id',
         ),
         name='public_offer'),
    path('privacy_policy/<str:guest_cabinet_id>/',
         GuestPdfView.as_view(
             template_name=HomeFolder.privacy_policy_file_name,
             user_name="Политика конфиденциальности.pdf",
             cabinet_id_url_kwarg='guest_cabinet_id',
         ),
         name='privacy_policy'),
    path('dyn_image/favicon/', FaviconImageView.as_view(), name='favicon_image'),
]
