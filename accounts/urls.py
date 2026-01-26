from django.urls import path
# from .views import
# from .views import TestProtectedView

from .views import (
    ForgotPasswordRequestView,
    ForgotPasswordVerifyOTPView,
    ResetPasswordView,
    LoginView,
    RegisterView,
    VerifyOTPView,
    TestProtectedView,
)

urlpatterns = [
    path("register/", RegisterView.as_view()),
    path("verify-otp/", VerifyOTPView.as_view()),
    path("login/", LoginView.as_view()),
    path("test-protected/", TestProtectedView.as_view(), name="test-protected"),
    path("forgot-password/", ForgotPasswordRequestView.as_view()),
    path("forgot-password/verify-otp/", ForgotPasswordVerifyOTPView.as_view()),
    path("forgot-password/reset/", ResetPasswordView.as_view()),
]
