import random
import threading
from django.core.mail import send_mail
from django.conf import settings
from rest_framework import serializers


# -------------------------------
# OTP GENERATOR
# -------------------------------
def generate_otp():
    return str(random.randint(100000, 999999))


# -------------------------------
# INTERNAL EMAIL SENDER
# -------------------------------
def _send_email(subject, message, email):
    try:
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
            fail_silently=True,
        )
    except Exception as e:
        print("Email error:", str(e))


# -------------------------------
# SEND OTP EMAIL (THREADED)
# -------------------------------
def send_otp_email(email, otp, purpose="register"):
    subject = f"Your OTP for {purpose.replace('_', ' ').title()}"
    message = (
        f"Hello,\n\n"
        f"Your OTP for {purpose.replace('_', ' ').title()} is: {otp}\n"
        f"It expires in 5 minutes.\n\n"
        f"Thank you."
    )

    threading.Thread(
        target=_send_email,
        args=(subject, message, email),
        daemon=True,
    ).start()


# -------------------------------
# VERIFY OTP WITH ATTEMPT LIMIT
# -------------------------------
def verify_otp_or_raise(otp_obj, input_otp):
    if otp_obj.attempts >= 5:
        raise serializers.ValidationError(
            "Too many attempts. Please request a new OTP."
        )

    if otp_obj.otp != input_otp:
        otp_obj.attempts += 1
        otp_obj.save(update_fields=["attempts"])

        raise serializers.ValidationError("Invalid OTP")

    return True


# import random
# import threading
# from django.core.mail import send_mail
# from django.conf import settings
# from rest_framework import serializers


# # -------------------------------
# # OTP GENERATOR
# # -------------------------------
# def generate_otp():
#     """
#     Generate a 6-digit numeric OTP
#     """
#     return str(random.randint(100000, 999999))


# # -------------------------------
# # SEND OTP EMAIL
# # -------------------------------
# def send_otp_email(email, otp, purpose="register"):
#     """
#     Send OTP email via Gmail SMTP.

#     Args:
#         email (str): Recipient email address
#         otp (str): OTP code
#         purpose (str): Purpose of OTP ('register', 'reset_password', 'change_email')
#     """

#     # Debug print (optional)
#     # print(f"[DEBUG] Sending OTP '{otp}' to {email} for purpose '{purpose}'")

#     # Create email subject and message
#     subject = f"Your OTP for {purpose.replace('_', ' ').title()}"
#     message = f"Hello,\n\nYour OTP for {purpose.replace('_', ' ').title()} is: {otp}\nIt expires in 5 minutes.\n\nThank you."

#     # Send email via SMTP
#     try:
#         send_mail(
#             subject=subject,
#             message=message,
#             from_email=settings.DEFAULT_FROM_EMAIL,  # Ensure this is your Gmail email
#             recipient_list=[email],
#             fail_silently=True,
#         )
#     except Exception as e:
#         print("Email error:", str(e))

#     threading.Thread(
#         target=send_otp_email,
#         args=(subject, message, email),
#     ).start()


# def verify_otp_or_raise(otp_obj, input_otp):
#     # max attempts
#     # print(
#     #     "(otp_obj.attempts, otp_obj.max_attempts :   _________" + otp_obj.attempts,
#     #     otp_obj.max_attempts,
#     # )
#     if otp_obj.attempts >= 5:
#         raise serializers.ValidationError(
#             "Too many attempts. Please request a new OTP."
#         )

#     # wrong otp
#     if otp_obj.otp != input_otp:
#         otp_obj.attempts += 1
#         otp_obj.save(update_fields=["attempts"])

#         raise serializers.ValidationError("Invalid OTP")

#     return True


# # import random
# # from django.core.mail import send_mail

# # from config import settings


# # def generate_otp():
# #     return str(random.randint(100000, 999999))


# # def send_otp_email(email, otp):
# #     print(f"Sending OTP {otp} to {email}")  # Debug only
# #     send_mail(
# #         subject="Your OTP Verification Code",
# #         message=f"Your OTP is {otp}. It expires in 5 minutes.",
# #         from_email=settings.DEFAULT_FROM_EMAIL,  # Use SMTP email
# #         recipient_list=[email],
# #         fail_silently=False,
# #     )
