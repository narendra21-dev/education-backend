from django.contrib.auth import authenticate
from django.db import transaction
from django.utils import timezone
from rest_framework import serializers
from .models import EmailOTP, User
from .utils import generate_otp, send_otp_email


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ("email", "username", "password")

    def create(self, validated_data):
        user = User.objects.create_user(
            email=validated_data["email"],
            username=validated_data["username"],
            password=validated_data["password"],
            is_active=False,  # important
        )

        otp = generate_otp()
        EmailOTP.objects.create(user=user, otp=otp)
        send_otp_email(user.email, otp)

        return user


class VerifyOTPSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.CharField(max_length=6)


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        user = authenticate(email=data["email"], password=data["password"])

        if not user:
            raise serializers.ValidationError("Invalid credentials")

        if not user.is_active:
            raise serializers.ValidationError("Account not verified")

        data["user"] = user
        return data


class ForgotPasswordRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate(self, data):
        try:
            user = User.objects.get(email=data["email"])
        except User.DoesNotExist:
            raise serializers.ValidationError("User not found")

        otp = generate_otp()

        with transaction.atomic():
            # Try to get an existing unverified OTP for this user
            otp_obj, created = EmailOTP.objects.get_or_create(
                user=user,
                purpose="reset_password",
                is_verified=False,
                defaults={"otp": otp},
            )

            # If it exists → update it
            if not created:
                otp_obj.otp = otp
                otp_obj.created_at = timezone.now()
                otp_obj.is_verified = False
                otp_obj.save()

        # Send OTP
        send_otp_email(user.email, otp)
        return data


class ForgotPasswordVerifyOTPSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.CharField(max_length=6)

    def validate(self, data):
        try:
            user = User.objects.get(email=data["email"])
        except User.DoesNotExist:
            raise serializers.ValidationError("User not found")

        otp_obj = (
            EmailOTP.objects.filter(
                user=user, purpose="reset_password", is_verified=False
            )
            .order_by("-created_at")
            .first()
        )

        if not otp_obj:
            raise serializers.ValidationError("OTP not found")

        if otp_obj.is_expired():
            raise serializers.ValidationError("OTP expired")

        if otp_obj.otp != data["otp"]:
            raise serializers.ValidationError("Invalid OTP")

        otp_obj.is_verified = True
        otp_obj.save()

        data["user"] = user
        return data


class ResetPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()
    new_password = serializers.CharField(min_length=8)

    def validate(self, data):
        try:
            user = User.objects.get(email=data["email"])
        except User.DoesNotExist:
            raise serializers.ValidationError("User not found")

        otp_obj = (
            EmailOTP.objects.filter(
                user=user, purpose="reset_password", is_verified=True
            )
            .order_by("-created_at")
            .first()
        )

        if not otp_obj:
            raise serializers.ValidationError("OTP verification required")

        data["user"] = user
        return data

    def save(self):
        user = self.validated_data["user"]
        user.set_password(self.validated_data["new_password"])
        user.save()

        # Optional: cleanup OTPs
        EmailOTP.objects.filter(user=user, purpose="reset_password").delete()
