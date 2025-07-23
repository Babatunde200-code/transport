from django.urls import path
from .views import BookingCreateView
from .views import UserBookingListView
urlpatterns = [
    path('book/', BookingCreateView.as_view(), name='book-ride'),
    path('api/booking/my-bookings/', UserBookingListView.as_view()),

]
