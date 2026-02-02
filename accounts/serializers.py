from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.password_validation import validate_password
from django.db import transaction
from django.utils import timezone
from rest_framework import serializers
from .models import EmailOTP
from .utils import generate_otp, send_otp_email, verify_otp_or_raise
from rest_framework.permissions import AllowAny

User = get_user_model()


# -------------------------------
# REGISTER SERIALIZER
# -------------------------------
class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True, required=True, validators=[validate_password]
    )

    class Meta:
        model = User
        fields = ("email", "username", "password")

    def create(self, validated_data):
        user = User.objects.create_user(
            email=validated_data["email"],
            username=validated_data["username"],
            password=validated_data["password"],
            role="student",
            is_active=False,  # Important for email verification
        )

        # Generate OTP
        otp = generate_otp()
        EmailOTP.objects.create(user=user, otp=otp, purpose="register")

        # Send OTP via SMTP
        send_otp_email(user.email, otp, purpose="register")

        return user


# -------------------------------
# VERIFY OTP SERIALIZER
# -------------------------------
class VerifyOTPSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.CharField(max_length=6)

    def validate(self, data):
        email = data["email"]
        input_otp = data["otp"].strip()  # ✅ IMPORTANT

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise serializers.ValidationError("User not found")

        otp_obj = (
            EmailOTP.objects.filter(user=user, purpose="register", is_verified=False)
            .order_by("-created_at")
            .first()
        )
        # print("DB OTP:", otp_obj.otp)
        # print("INPUT OTP:", input_otp)

        if not otp_obj:
            raise serializers.ValidationError("OTP not found")

        if otp_obj.is_expired():
            raise serializers.ValidationError("OTP expired")

        verify_otp_or_raise(otp_obj, data["otp"])

        # ✅ Mark OTP verified
        otp_obj.is_verified = True
        otp_obj.save()

        # ✅ Activate user
        user.is_active = True
        user.save()

        data["user"] = user
        return data


# -------------------------------
# RESEND REGISTER OTP SERIALIZER
# -------------------------------


class ResendRegisterOTPSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate(self, data):
        user = User.objects.filter(email=data["email"], is_active=False).first()

        if not user:
            raise serializers.ValidationError("User not found or already verified")

        # delete old OTP
        EmailOTP.objects.filter(
            user=user, purpose="register", is_verified=False
        ).delete()

        otp = generate_otp()

        otp_obj, _ = EmailOTP.objects.update_or_create(
            user=user,
            purpose="register",
            defaults={
                "otp": otp,
                "is_verified": False,
                "attempts": 0,
                "created_at": timezone.now(),  # 🔥 IMPORTANT
            },
        )

        send_otp_email(user.email, otp, purpose="register")
        return data


# -------------------------------
# LOGIN SERIALIZER
# -------------------------------
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


# -------------------------------
# FORGOT PASSWORD REQUEST
# -------------------------------
class ForgotPasswordRequestSerializer(serializers.Serializer):
    # permission_classes = [AllowAny]
    email = serializers.EmailField()

    def validate(self, data):
        try:
            user = User.objects.get(email=data["email"])
        except User.DoesNotExist:
            raise serializers.ValidationError("User not found")

        EmailOTP.objects.filter(
            user=user, purpose="reset_password", is_verified=False
        ).delete()

        otp = generate_otp()
        with transaction.atomic():
            otp_obj, created = EmailOTP.objects.get_or_create(
                user=user,
                purpose="reset_password",
                is_verified=False,
                defaults={"otp": otp},
            )

            if not created:
                otp_obj.otp = otp
                otp_obj.created_at = timezone.now()
                otp_obj.is_verified = False
                otp_obj.save()

        send_otp_email(user.email, otp, purpose="reset_password")
        return data


# -------------------------------
# FORGOT PASSWORD VERIFY OTP
# -------------------------------
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
        verify_otp_or_raise(otp_obj, data["otp"])

        if not otp_obj:
            raise serializers.ValidationError("OTP not found")
        if otp_obj.is_expired():
            raise serializers.ValidationError("OTP expired")
        # if otp_obj.otp != data["otp"]:
        #     raise serializers.ValidationError("Invalid OTP")
        # verify_otp_or_raise(otp_obj, data["otp"])

        otp_obj.is_verified = True
        otp_obj.save()

        data["user"] = user
        return data


# -------------------------------
# RESET PASSWORD
# -------------------------------
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
        if otp_obj.is_expired():
            raise serializers.ValidationError("OTP expired")

        # Optional: validate password strength
        validate_password(data["new_password"], user=user)

        data["user"] = user
        return data

    def save(self):
        user = self.validated_data["user"]
        user.set_password(self.validated_data["new_password"])
        user.save()

        # Clean up old OTPs
        EmailOTP.objects.filter(user=user, purpose="reset_password").delete()


# -------------------------------
# PROFILE SERIALIZER
# -------------------------------
class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("email", "username", "profile_image", "role")
        read_only_fields = ("email", "role")


# -------------------------------
# EMAIL CHANGE REQUEST
# -------------------------------


class RequestEmailChangeSerializer(serializers.Serializer):
    new_email = serializers.EmailField()

    def validate(self, data):
        user = self.context["request"].user

        # delete old OTPs
        EmailOTP.objects.filter(
            user=user, purpose="change_email", is_verified=False
        ).delete()

        otp = generate_otp()

        EmailOTP.objects.update_or_create(
            user=user, otp=otp, purpose="change_email", email=data["new_email"]
        )

        send_otp_email(data["new_email"], otp, purpose="change_email")

        return data


# -------------------------------
# EMAIL CHANGE VERIFY OTP
# -------------------------------


class VerifyEmailChangeSerializer(serializers.Serializer):
    otp = serializers.CharField(max_length=6)

    def validate(self, data):
        user = self.context["request"].user

        otp_obj = (
            EmailOTP.objects.filter(
                user=user, purpose="change_email", is_verified=False
            )
            .order_by("-created_at")
            .first()
        )

        if not otp_obj:
            raise serializers.ValidationError("OTP not found")

        if otp_obj.is_expired():
            raise serializers.ValidationError("OTP expired")

        verify_otp_or_raise(otp_obj, data["otp"])

        data["otp_obj"] = otp_obj
        return data

    def save(self):
        otp_obj = self.validated_data["otp_obj"]
        user = otp_obj.user

        # update email
        user.email = otp_obj.email
        user.username = otp_obj.email
        user.save()

        otp_obj.is_verified = True
        otp_obj.save()

        EmailOTP.objects.filter(user=user, purpose="change_email").exclude(
            id=otp_obj.id
        ).delete()

        return user


# -------------------------------
# RESEND OTP SERIALIZER
# -------------------------------


class ResendOTPSerializer(serializers.Serializer):
    email = serializers.EmailField()
    purpose = serializers.ChoiceField(
        choices=["register", "reset_password", "change_email"]
    )

    def validate(self, data):
        try:
            user = User.objects.get(email=data["email"])
        except User.DoesNotExist:
            return data  # hide existence

        EmailOTP.objects.filter(
            user=user, purpose=data["purpose"], is_verified=False
        ).delete()

        otp = generate_otp()

        EmailOTP.objects.create(
            user=user, otp=otp, purpose=data["purpose"], attempts=0, is_locked=False
        )

        send_otp_email(user.email, otp, data["purpose"])
        return data


# class ResendOTPSerializer(serializers.Serializer):
#     purpose = serializers.ChoiceField(
#         choices=["register", "reset_password", "change_email"]
#     )

#     def validate(self, data):
#         user = self.context["request"].user

#         EmailOTP.objects.filter(
#             user=user, purpose=data["purpose"], is_verified=False
#         ).delete()

#         otp = generate_otp()

#         EmailOTP.objects.create(user=user, otp=otp, purpose=data["purpose"])

#         send_otp_email(user.email, otp, data["purpose"])

#         return data


# class VerifyEmailChangeSerializer(serializers.Serializer):
#     otp = serializers.CharField(max_length=6)

#     def validate(self, data):
#         user = self.context["request"].user

#         # 🔥 delete old unverified OTP
#         EmailOTP.objects.filter(
#             user=user, purpose="change_email", is_verified=False
#         ).delete()

#         otp = generate_otp()

#         EmailOTP.objects.update_or_create(
#             user=user, otp=otp, purpose="change_email", email=data["new_email"]
#         )

#         send_otp_email(data["new_email"], otp, purpose="change_email")
#         return data


# class VerifyEmailChangeSerializer(serializers.Serializer):
#     otp = serializers.CharField(max_length=6)

# def validate(self, data):
#     user = self.context["request"].user

#     otp_obj = (
#         EmailOTP.objects.filter(
#             user=user, purpose="change_email", is_verified=False
#         )
#         .order_by("-created_at")
#         .first()
#     )

#     if not otp_obj:
#         raise serializers.ValidationError("OTP not found")
#     if otp_obj.is_expired():
#         raise serializers.ValidationError("OTP expired")
#     if otp_obj.otp != data["otp"]:
#         raise serializers.ValidationError("Invalid OTP")

#     # Update user email after successful verification
#     user.email = otp_obj.email
#     user.save()

#     otp_obj.is_verified = True
#     otp_obj.save()

#     data["user"] = user
#     return data


# from django.contrib.auth import authenticate
# from django.db import transaction
# from django.utils import timezone
# from rest_framework import serializers
# from .models import EmailOTP, User
# from .utils import generate_otp, send_otp_email
# from django.contrib.auth import get_user_model
# from django.contrib.auth.password_validation import validate_password


# User = get_user_model()


# class RegisterSerializer(serializers.ModelSerializer):
#     # password = serializers.CharField(write_only=True)
#     password = serializers.CharField(
#         write_only=True, required=True, validators=[validate_password]
#     )

#     class Meta:
#         model = User
#         fields = ("email", "username", "password")

#     def create(self, validated_data):
#         user = User.objects.create_user(
#             email=validated_data["email"],
#             username=validated_data["username"],
#             password=validated_data["password"],
#             role="student",  # FORCE STUDENT
#             is_active=False,  # important
#         )

#         # otp = generate_otp()
#         # EmailOTP.objects.create(user=user, otp=otp)
#         # send_otp_email(user.email, otp)

#         # Generate OTP
#         otp = generate_otp()
#         EmailOTP.objects.create(user=user, otp=otp, purpose="register")

#         # Send email via SMTP
#         send_otp_email(user.email, otp, purpose="register")

#         return user


# class VerifyOTPSerializer(serializers.Serializer):
#     email = serializers.EmailField()
#     otp = serializers.CharField(max_length=6)


# class LoginSerializer(serializers.Serializer):
#     email = serializers.EmailField()
#     password = serializers.CharField(write_only=True)

#     def validate(self, data):
#         user = authenticate(email=data["email"], password=data["password"])

#         if not user:
#             raise serializers.ValidationError("Invalid credentials")

#         if not user.is_active:
#             raise serializers.ValidationError("Account not verified")

#         data["user"] = user
#         return data


# class ForgotPasswordRequestSerializer(serializers.Serializer):
#     email = serializers.EmailField()

#     def validate(self, data):
#         try:
#             user = User.objects.get(email=data["email"])
#         except User.DoesNotExist:
#             raise serializers.ValidationError("User not found")

#         otp = generate_otp()

#         with transaction.atomic():
#             # Try to get an existing unverified OTP for this user
#             otp_obj, created = EmailOTP.objects.get_or_create(
#                 user=user,
#                 purpose="reset_password",
#                 is_verified=False,
#                 defaults={"otp": otp},
#             )

#             # If it exists → update it
#             if not created:
#                 otp_obj.otp = otp
#                 otp_obj.created_at = timezone.now()
#                 otp_obj.is_verified = False
#                 otp_obj.save()

#         # Send OTP
#         send_otp_email(user.email, otp, purpose="reset_password")
#         return data


# class ForgotPasswordVerifyOTPSerializer(serializers.Serializer):
#     email = serializers.EmailField()
#     otp = serializers.CharField(max_length=6)

#     def validate(self, data):
#         try:
#             user = User.objects.get(email=data["email"])
#         except User.DoesNotExist:
#             raise serializers.ValidationError("User not found")

#         otp_obj = (
#             EmailOTP.objects.filter(
#                 user=user, purpose="reset_password", is_verified=False
#             )
#             .order_by("-created_at")
#             .first()
#         )

#         if not otp_obj:
#             raise serializers.ValidationError("OTP not found")

#         if otp_obj.is_expired():
#             raise serializers.ValidationError("OTP expired")

#         if otp_obj.otp != data["otp"]:
#             raise serializers.ValidationError("Invalid OTP")

#         otp_obj.is_verified = True
#         otp_obj.save()

#         # data["user"] = user
#         validate_password(data["new_password"], user=user)
#         return data


# class ResetPasswordSerializer(serializers.Serializer):
#     email = serializers.EmailField()
#     new_password = serializers.CharField(min_length=8)

#     def validate(self, data):
#         try:
#             user = User.objects.get(email=data["email"])
#         except User.DoesNotExist:
#             raise serializers.ValidationError("User not found")

#         otp_obj = (
#             EmailOTP.objects.filter(
#                 user=user, purpose="reset_password", is_verified=True
#             )
#             .order_by("-created_at")
#             .first()
#         )

#         if not otp_obj:
#             raise serializers.ValidationError("OTP verification required")

#         data["user"] = user
#         return data

#     def save(self):
#         user = self.validated_data["user"]
#         user.set_password(self.validated_data["new_password"])
#         user.save()

#         # Optional: cleanup OTPs
#         EmailOTP.objects.filter(user=user, purpose="reset_password").delete()


# class ProfileSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = User
#         fields = ("email", "username", "profile_image", "role")
#         read_only_fields = ("email", "role")


# class RequestEmailChangeSerializer(serializers.Serializer):
#     new_email = serializers.EmailField()


# class VerifyEmailChangeSerializer(serializers.Serializer):
#     otp = serializers.CharField(max_length=6)
