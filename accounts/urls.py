from django.urls import path
from .views import (
    SignupView,
    VerifyAccountView,
    ResendVerificationView,
    LoginView,
    ProfileView,
    MakeAdminView,
    ForgotPasswordView,
    ResetPasswordView,
)

urlpatterns = [
    path("signup/", SignupView.as_view(), name="signup"),
    path("verify/", VerifyAccountView.as_view(), name="verify"),
    path("resend-code/", ResendVerificationView.as_view(), name="resend_code"),
    path("login/", LoginView.as_view(), name="login"),
    path("profile/", ProfileView.as_view(), name="profile"),
    path("make-admin/", MakeAdminView.as_view(), name="make-admin"),
    path("forgot-password/", ForgotPasswordView.as_view(), name="forgot-password"),
    path("reset-password/", ResetPasswordView.as_view(), name="reset-password"),
]
