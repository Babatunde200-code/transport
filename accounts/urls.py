from django.urls import path
from .views import SignupView, LoginView, VerifyAccountView
from .views import ProfileView, ProfilePhotoUploadView
from .views import ProfileView, ProfilePhotoUploadView


urlpatterns = [
    path('signup/', SignupView.as_view()),
    path('login/', LoginView.as_view()),
    path('verify/', VerifyAccountView.as_view()),
    path('profile/', ProfileView.as_view()),
    path('profile/upload-photo/', ProfilePhotoUploadView.as_view()),
]
