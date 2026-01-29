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
    ResetPasswordSerializer,
    VerifyEmailChangeSerializer,
)
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from .models import EmailOTP
from .serializers import VerifyOTPSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import get_user_model
from .utils import generate_otp, send_otp_email

User = get_user_model()


class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            {"message": "OTP sent to email (check console)"},
            status=status.HTTP_201_CREATED,
        )


User = get_user_model()


class VerifyOTPView(generics.GenericAPIView):
    serializer_class = VerifyOTPSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data["email"]
        otp = serializer.validated_data["otp"]

        user = User.objects.filter(email=email).first()
        if not user:
            return Response({"error": "User not found"}, status=404)

        otp_obj = EmailOTP.objects.filter(user=user, otp=otp, is_verified=False).last()

        if not otp_obj:
            return Response({"error": "Invalid OTP"}, status=400)

        if otp_obj.is_expired():
            return Response({"error": "OTP expired"}, status=400)

        otp_obj.is_verified = True
        otp_obj.save()

        user.is_active = True
        user.save()

        return Response({"message": "Account verified successfully"})


class LoginView(APIView):
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data["user"]
        refresh = RefreshToken.for_user(user)

        return Response(
            {
                "access": str(refresh.access_token),
                "refresh": str(refresh),
                "user": {
                    "id": user.id,
                    "email": user.email,
                    "username": user.username,
                },
            },
            status=status.HTTP_200_OK,
        )


class TestProtectedView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response({"message": "JWT working", "user": request.user.email})


class ForgotPasswordRequestView(APIView):
    def post(self, request):
        serializer = ForgotPasswordRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(
            {"message": "OTP sent to your email"},
            status=status.HTTP_200_OK,
        )


class ForgotPasswordVerifyOTPView(APIView):
    def post(self, request):
        serializer = ForgotPasswordVerifyOTPSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(
            {"message": "OTP verified successfully"},
            status=status.HTTP_200_OK,
        )


class ResetPasswordView(APIView):
    def post(self, request):
        serializer = ResetPasswordSerializer(data=request.data)
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
class RequestEmailChangeView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = RequestEmailChangeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        new_email = serializer.validated_data["new_email"]

        if User.objects.filter(email=new_email).exists():
            return Response(
                {"message": "Email already in use"}, status=status.HTTP_400_BAD_REQUEST
            )

        otp = generate_otp()

        # EmailOTP.objects.create(
        #     user=request.user, otp=otp, purpose="change_email", email=new_email
        # )
        # delete previous unverified otp for same purpose
        EmailOTP.objects.filter(
            user=request.user, purpose="change_email", is_verified=False
        ).delete()

        # create fresh otp
        EmailOTP.objects.create(
            user=request.user, otp=otp, purpose="change_email", email=new_email
        )

        send_otp_email(new_email, otp)

        return Response({"message": "OTP sent to new email"}, status=status.HTTP_200_OK)


# -------------------------------
# Verify Email Change
# -------------------------------
class VerifyEmailChangeView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = VerifyEmailChangeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        otp_code = serializer.validated_data["otp"]

        try:
            record = EmailOTP.objects.get(
                user=request.user,
                otp=otp_code,
                purpose="change_email",
                is_verified=False,
            )
        except EmailOTP.DoesNotExist:
            return Response(
                {"message": "Invalid OTP"}, status=status.HTTP_400_BAD_REQUEST
            )

        if record.is_expired():
            return Response(
                {"message": "OTP expired"}, status=status.HTTP_400_BAD_REQUEST
            )

        request.user.email = record.email
        request.user.save()

        record.is_verified = True
        record.save()

        return Response(
            {"message": "Email updated successfully"}, status=status.HTTP_200_OK
        )
