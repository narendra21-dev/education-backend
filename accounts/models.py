from django.db import models

# Create your models here.

from django.contrib.auth.models import AbstractUser
from django.conf import settings
from django.utils import timezone
from cloudinary.models import CloudinaryField


class User(AbstractUser):
    ROLE_CHOICES = (
        ("student", "Student"),
        ("teacher", "Teacher"),
    )

    email = models.EmailField(unique=True)
    profile_image = CloudinaryField("image", folder="profiles", blank=True, null=True)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default="student")

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    def save(self, *args, **kwargs):
        # Do NOT override superusers
        if self.is_superuser:
            self.is_staff = True
            self.role = "teacher"
        else:
            if self.role == "teacher":
                self.is_staff = True
            else:
                self.is_staff = False

        super().save(*args, **kwargs)

    def __str__(self):
        return self.email


class EmailOTP(models.Model):
    PURPOSE_CHOICES = (
        ("register", "Register"),
        ("reset_password", "Reset Password"),
        ("change_email", "Change Email"),
    )

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    otp = models.CharField(max_length=6)
    attempts = models.PositiveIntegerField(default=0)
    max_attempts = 5
    purpose = models.CharField(
        max_length=20,
        choices=PURPOSE_CHOICES,
        default="register",  # ✅ IMPORTANT
    )

    created_at = models.DateTimeField(auto_now_add=True)
    is_verified = models.BooleanField(default=False)
    email = models.EmailField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["user", "purpose", "is_verified"],
                condition=models.Q(is_verified=False),
                name="one_active_otp_per_user_purpose",
            )
        ]

    def is_expired(self):
        return timezone.now() > self.created_at + timezone.timedelta(minutes=5)

    def __str__(self):
        return f"{self.user.email} - {self.otp} ({self.purpose})"

    # email = models.EmailField(null=True, blank=True)
