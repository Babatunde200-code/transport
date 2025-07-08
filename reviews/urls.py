from django.urls import path
from .views import ReviewListCreateView, ReviewDetailView, DriverReviewsView

urlpatterns = [
    path('', ReviewListCreateView.as_view()),  # POST + GET ?travel=<id>
    path('<int:pk>/', ReviewDetailView.as_view()),  # PUT, DELETE
    path('driver/<int:user_id>/', DriverReviewsView.as_view()),  # GET
]
