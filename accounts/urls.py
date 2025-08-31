from django.urls import path
from .views import SignupView, VerifyAccountView, LoginView


urlpatterns = [
    path("signup/", SignupView.as_view(), name="signup"),
    path("verify/", VerifyAccountView.as_view(), name="verify"),
    path("login/", LoginView.as_view()),
]
