from django.urls import path
# from .views import
# from .views import TestProtectedView

from .views import (
    ForgotPasswordRequestView,
    ForgotPasswordVerifyOTPView,
    ProfileView,
    RequestEmailChangeView,
    ResendRegisterOTPView,
    ResetPasswordView,
    LoginView,
    RegisterView,
    VerifyEmailChangeView,
    VerifyOTPView,
    TestProtectedView,
    test_email,
    MeView,
)

urlpatterns = [
    path("register/", RegisterView.as_view()),
    path("verify-otp/", VerifyOTPView.as_view()),
    path("login/", LoginView.as_view()),
    path("test-protected/", TestProtectedView.as_view(), name="test-protected"),
    path("forgot-password/", ForgotPasswordRequestView.as_view()),
    path("forgot-password/verify-otp/", ForgotPasswordVerifyOTPView.as_view()),
    path("forgot-password/reset/", ResetPasswordView.as_view()),
    path("profile/", ProfileView.as_view()),
    path("request-email-change/", RequestEmailChangeView.as_view()),
    path("verify-email-change/", VerifyEmailChangeView.as_view()),
    path(
        "resend-register-otp/",
        ResendRegisterOTPView.as_view(),
        name="resend-register-otp",
    ),
    path("test-email/", test_email),
    path("me/", MeView.as_view(), name="me"),
]
