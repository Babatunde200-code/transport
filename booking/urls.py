from django.urls import path
from .views import BookingListCreateView, BookingCancelView
from .views import (
    BookingListCreateView, BookingCancelView,
    driver_booking_list, approve_booking, decline_booking
)

urlpatterns = [
    path('', BookingListCreateView.as_view()),
    path('<int:pk>/', BookingCancelView.as_view()),
    path('driver/', driver_booking_list),
    path('driver/<int:pk>/approve/', approve_booking),
    path('driver/<int:pk>/decline/', decline_booking),
]
