from django.urls import path
from .views import (
    SignupView,
    VerifyAccountView,
    ResendVerificationView,
    LoginView,
    ProfileView,
    MakeAdminView,
)

urlpatterns = [
    path("signup/", SignupView.as_view(), name="signup"),
    path("verify/", VerifyAccountView.as_view(), name="verify"),
    path("resend-code/", ResendVerificationView.as_view(), name="resend_code"),
    path("login/", LoginView.as_view(), name="login"),
    path("profile/", ProfileView.as_view(), name="profile"),
    path("make-admin/", MakeAdminView.as_view(), name="make-admin"),
]
