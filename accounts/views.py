# from django.shortcuts import render

# Create your views here.

from rest_framework import generics, status
from rest_framework.response import Response
from .serializers import (
    ForgotPasswordRequestSerializer,
    ForgotPasswordVerifyOTPSerializer,
    LoginSerializer,
    ProfileSerializer,
    RegisterSerializer,
    RequestEmailChangeSerializer,
    ResendOTPSerializer,
    ResendRegisterOTPSerializer,
    ResetPasswordSerializer,
    VerifyEmailChangeSerializer,
)
from rest_framework.views import APIView
from rest_framework.generics import GenericAPIView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from .models import EmailOTP
from .serializers import VerifyOTPSerializer
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import get_user_model
from .utils import generate_otp, send_otp_email
from .throttles import OTPThrottle
from django.core.mail import send_mail
from rest_framework.decorators import api_view
from django.conf import settings
from drf_spectacular.utils import extend_schema


User = get_user_model()


class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            {"message": "OTP sent to email (check)"},
            status=status.HTTP_201_CREATED,
        )


User = get_user_model()


class VerifyOTPView(generics.GenericAPIView):
    # serializer_class = VerifyOTPSerializer
    serializer_class = VerifyOTPSerializer
    throttle_classes = [OTPThrottle]

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response({"message": "OTP verified"})


class ResendRegisterOTPView(generics.GenericAPIView):
    serializer_class = ResendRegisterOTPSerializer
    throttle_classes = [OTPThrottle]

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response({"message": "OTP resent successfully"})


# class ResendRegisterOTPView(APIView):
#     permission_classes = []  # 🔓 Public endpoint
#     throttle_classes = [OTPThrottle]

#     def post(self, request):
#         serializer = ResendRegisterOTPSerializer(data=request.data)
#         serializer.is_valid(raise_exception=True)

#         return Response(
#             {"message": "OTP resent successfully"},
#             status=status.HTTP_200_OK,
#         )


class LoginView(APIView):
    @extend_schema(request=LoginSerializer, responses={200: dict})
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data["user"]
        refresh = RefreshToken.for_user(user)

        # 🔥 ADD CLAIMS INTO THE ACCESS TOKEN
        refresh.access_token["email"] = user.email
        refresh.access_token["is_staff"] = user.is_staff
        refresh.access_token["is_superuser"] = user.is_superuser

        return Response(
            {
                "access": str(refresh.access_token),
                "refresh": str(refresh),
                "user": {
                    "id": user.id,
                    "email": user.email,
                    "username": user.username,
                    "is_staff": user.is_staff,
                },
            },
            status=status.HTTP_200_OK,
        )


class TestProtectedView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response({"message": "JWT working", "user": request.user.email})


class ForgotPasswordRequestView(APIView):
    serializer_class = ForgotPasswordRequestSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        # serializer = ForgotPasswordRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(
            {"message": "OTP sent to your email"},
            status=status.HTTP_200_OK,
        )


class ForgotPasswordVerifyOTPView(APIView):
    serializer_class = ForgotPasswordVerifyOTPSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        # serializer = ForgotPasswordVerifyOTPSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(
            {"message": "OTP verified successfully"},
            status=status.HTTP_200_OK,
        )


class ResetPasswordView(APIView):
    serializer_class = ResetPasswordSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        # serializer = ResetPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data["user"]
        new_password = serializer.validated_data["new_password"]

        # Update password
        user.set_password(new_password)
        user.save()

        # ✅ Delete all reset_password OTPs (verified or not)
        EmailOTP.objects.filter(user=user, purpose="reset_password").delete()

        return Response(
            {"message": "Password reset successful"},
            status=status.HTTP_200_OK,
        )


class ProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = ProfileSerializer(request.user)
        return Response(serializer.data)

    def patch(self, request):
        serializer = ProfileSerializer(request.user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            {"message": "Profile updated successfully", "user": serializer.data}
        )


# -------------------------------
# Request Email Change
# -------------------------------


class RequestEmailChangeView(GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = RequestEmailChangeSerializer

    def post(self, request):
        serializer = self.get_serializer(
            data=request.data,
            context={"request": request},  # 🔥 REQUIRED
        )
        serializer.is_valid(raise_exception=True)

        return Response({"message": "OTP sent to new email"})


# -------------------------------
# Verify Email Change
# -------------------------------


class VerifyEmailChangeView(GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = VerifyEmailChangeSerializer

    def get_serializer_context(self):
        return {"request": self.request}

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response({"message": "Email updated successfully"}, status=200)


class ResendOTPView(GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ResendOTPSerializer
    throttle_classes = [OTPThrottle]

    def get_serializer_context(self):
        return {"request": self.request}

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response({"message": "OTP resent successfully"})


@api_view(["GET"])
def test_email(request):
    send_otp_email("devn22827@gmail.com", "123456")
    return Response({"message": "Email sent successfully"})


# -------------------------------
# MeView - Get current user info
# -------------------------------


class MeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        print("user.email : ______", user)
        print("user.email, : ______", user.email, user.is_staff, user.is_superuser)

        return Response(
            {
                "email": user.email,
                "is_staff": user.is_staff,
                "is_superuser": user.is_superuser,
            }
        )
