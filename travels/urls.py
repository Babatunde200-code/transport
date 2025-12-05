from django.urls import path
from . import views
from .views import (
    AdminSignupView,
    AdminLoginView,
    AdminRideView,
    RideListView,
    BookRideView,
    UserBookingsView,
    BookingDetailView,
    MarkPaidView,
    DashboardBookingsView,
    DashboardPaymentsView,
    DashboardPendingPaymentsView
)

urlpatterns = [

    # -------------------------
    # ADMIN AUTH & RIDE MGMT
    # -------------------------
    path("admin/signup/", AdminSignupView.as_view(), name="admin-signup"),
    path("admin/login/", AdminLoginView.as_view(), name="admin-login"),

    # Admin creates/updates/deletes rides
    path("admin/rides/", AdminRideView.as_view(), name="admin-ride-create"),
    path("admin/rides/<str:ride_id>/", AdminRideView.as_view(), name="admin-ride-update-delete"),

    # -------------------------
    # USER RIDE ACTIONS
    # -------------------------
    path("rides/", RideListView.as_view(), name="ride-list"),
    path("rides/<str:ride_id>/book/", BookRideView.as_view(), name="book-ride"),

    # -------------------------
    # USER BOOKINGS
    # -------------------------
    path("bookings/", UserBookingsView.as_view(), name="user-bookings"),
    path("bookings/<str:booking_id>/", BookingDetailView.as_view(), name="booking-detail"),
    path("bookings/<str:booking_id>/pay/", MarkPaidView.as_view(), name="mark-paid"),

    # Flutterwave Webhook/Verification
    path("verify-payment/", views.verify_payment, name="verify-payment"),

    # -------------------------
    # USER DASHBOARD API
    # -------------------------
    path("dashboard/bookings/", DashboardBookingsView.as_view(), name="dashboard-bookings"),
    path("dashboard/payments/", DashboardPaymentsView.as_view(), name="dashboard-payments"),
    path("dashboard/payments/pending/", DashboardPendingPaymentsView.as_view(), name="dashboard-pending-payments"),
]
