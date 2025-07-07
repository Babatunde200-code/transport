from django.urls import path
from .views import TravelListCreateView, TravelDetailView

urlpatterns = [
    path('', TravelListCreateView.as_view()),
    path('<int:pk>/', TravelDetailView.as_view()),
]
