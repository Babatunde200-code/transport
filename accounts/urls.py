from django.urls import path
from .views import SignupView, LoginView, VerifyAccountView
from .views import ProfileView, ProfilePhotoUploadView
from .views import ProfileView, ProfilePhotoUploadView
from .views import PasswordResetRequestView, PasswordResetConfirmView
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path('signup/', SignupView.as_view()),
    path('login/', LoginView.as_view()),
    path('verify/', VerifyAccountView.as_view()),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('profile/', ProfileView.as_view()),
    path('profile/upload-photo/', ProfilePhotoUploadView.as_view()),
     path('password-reset/', PasswordResetRequestView.as_view()),
    path('reset-password/<int:uid>/<str:token>/', PasswordResetConfirmView.as_view()),
]
