# from django.contrib import admin

# # Register your models here.

# from django.contrib import admin
# from .models import User, EmailOTP

# admin.site.register(User)
# admin.site.register(EmailOTP)


from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import EmailOTP, User


# @admin.register(User)
# class CustomUserAdmin(UserAdmin):
#     model = User

#     list_display = ("email", "username", "role", "is_staff", "is_active")
#     ordering = ("email",)

#     fieldsets = (
#         (None, {"fields": ("email", "password")}),
#         ("Personal Info", {"fields": ("username", "profile_image", "role")}),
#         (
#             "Permissions",
#             {
#                 "fields": (
#                     "is_active",
#                     "is_staff",
#                     "is_superuser",
#                     "groups",
#                     "user_permissions",
#                 )
#             },
#         ),
#         ("Dates", {"fields": ("last_login", "date_joined")}),
#     )

#     add_fieldsets = (
#         (
#             None,
#             {
#                 "classes": ("wide",),
#                 "fields": (
#                     "email",
#                     "username",
#                     "role",
#                     "password1",
#                     "password2",
#                     "is_staff",
#                     "is_superuser",
#                 ),
#             },
#         ),
#     )

#     search_fields = ("email", "username")


# @admin.register(EmailOTP)
# class EmailOTPAdmin(admin.ModelAdmin):
#     list_display = ("user", "otp", "is_verified", "created_at")
#     list_filter = ("is_verified",)
#     search_fields = ("user__email",)


from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, EmailOTP
from django.utils.html import format_html


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    model = User

    list_display = (
        "id",
        "email",
        "username",
        "role",
        "profile_preview",  # NEW
        "is_staff",
        "is_active",
    )
    list_filter = ("role", "is_staff", "is_active")
    ordering = ("email",)
    search_fields = ("email", "username")

    fieldsets = (
        (None, {"fields": ("email", "password")}),
        (
            "Personal Info",
            {"fields": ("username", "profile_image", "role")},
        ),
        (
            "Permissions",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                )
            },
        ),
        ("Important Dates", {"fields": ("last_login", "date_joined")}),
    )

    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "email",
                    "username",
                    "role",
                    "password1",
                    "password2",
                    "is_staff",
                    "is_superuser",
                    "is_active",
                ),
            },
        ),
    )

    def profile_preview(self, obj):
        if obj.profile_image:
            return format_html(
                '<img src="{}" width="40" height="40" style="border-radius:50%;" />',
                obj.profile_image.url,
            )
        return "No Image"

    profile_preview.short_description = "Profile"


@admin.register(EmailOTP)
class EmailOTPAdmin(admin.ModelAdmin):
    list_display = ("user", "otp", "purpose", "is_verified", "created_at")
    list_filter = ("purpose", "is_verified")
    search_fields = ("user__email",)
