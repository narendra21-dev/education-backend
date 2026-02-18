from pyexpat.errors import messages
from django.shortcuts import redirect, render
import requests
from django.conf import settings
from django.contrib.auth.decorators import login_required
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response

from education.models import Book, Paper, University, Course
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required

from education.serializers import BookSerializer


API_BASE_URL = "https://education-backend-2-qmvp.onrender.com/api"


# Create your views here.


def home(request):
    return render(request, "website/landing.html")


# -----------------------------
# Landing Page
# -----------------------------
# def landing(request):
#     return render(request, "website/landing.html")


# -----------------------------
# Dashboard Page
# -----------------------------
def dashboard(request):
    # JS will check JWT in localStorage
    return render(request, "website/dashboard.html")


# -----------------------------
# Auth Pages
# -----------------------------
def login_view(request):
    return render(request, "website/auth/login.html")


def register_view(request):
    return render(request, "website/auth/register.html")


def verify_otp_view(request):
    return render(request, "website/auth/verify_otp.html")


def forgot_password(request):
    if request.method == "POST":
        email = request.POST["email"]

        res = requests.post(
            f"{API_BASE_URL}/accounts/forgot-password/", json={"email": email}
        )

        if res.status_code == 200:
            request.session["fp_email"] = email
            return redirect("/forgot-password/verify/")

        messages.error(request, res.json()["detail"])

    return render(request, "website/auth/forgot_password.html")


def verify_forgot_otp(request):
    email = request.session.get("fp_email")
    if not email:
        return redirect("/login/")

    if request.method == "POST":
        otp = request.POST["otp"]

        res = requests.post(
            f"{API_BASE_URL}/accounts/forgot-password/verify-otp/",
            json={"email": email, "otp": otp},
        )
        # print("email, otp: ___" + email, otp)
        # print("URL : ______" + f"{API_BASE_URL}/accounts/verify-forgot-otp/")

        if res.status_code == 200:
            return redirect("/forgot-password/reset/")

        messages.error(request, res.json()["detail"])

    return render(request, "website/auth/verify_forgot_otp.html")


def reset_password(request):
    email = request.session.get("fp_email")
    if not email:
        return redirect("/login/")

    if request.method == "POST":
        password = request.POST["password"]

        res = requests.post(
            f"{API_BASE_URL}/accounts/forgot-password/reset/",
            json={"email": email, "new_password": password},
        )

        if res.status_code == 200:
            del request.session["fp_email"]
            # messages.success(request, "Password reset successfully")
            return redirect("/login/")

        messages.error(request, res.json()["detail"])

    return render(request, "website/auth/reset_password.html")


# -----------------------------
# Browse Pages (API-driven)
# JS fetches data from Render backend
# -----------------------------


@login_required
def universities(request):
    return render(request, "website/browse/universities.html")


def courses(request):
    return render(request, "website/browse/courses.html")


def periods(request):
    return render(request, "website/browse/periods.html")


def books(request):
    period_id = request.GET.get("period")

    if not period_id:
        return redirect("periods")

    return render(request, "website/browse/books.html", {"period_id": period_id})


def units(request):
    book_id = request.GET.get("book")

    return render(request, "website/browse/units.html", {"book_id": book_id})


def chapters(request):
    unit_id = request.GET.get("unit")

    return render(request, "website/browse/chapters.html", {"unit_id": unit_id})


def chapter_details(request):
    chapter_id = request.GET.get("chapter")

    return render(
        request, "website/browse/chapter-details.html", {"chapter_id": chapter_id}
    )


def questions_page(request):
    return render(request, "website/browse/questions.html")


def papers_page(request):
    return render(request, "website/browse/papers.html")


def pdf_preview(request, paper_id):
    paper = Paper.objects.get(id=paper_id)

    return render(request, "website/browse/pdf_viewer.html", {"pdf_url": paper.pdf.url})


def notes_page(request):
    # paper = Paper.objects.get(id=paper_id)

    return render(request, "website/browse/notes.html")


def note_detail(request):
    # paper = Paper.objects.get(id=paper_id)

    return render(request, "website/browse/note_detail.html")


@api_view(["GET"])
def books_by_period(request, period_id):
    books = Book.objects.filter(period_id=period_id)
    serializer = BookSerializer(books, many=True)
    return Response(serializer.data)


# @api_view(["GET"])
# @permission_classes([IsAdminUser])
# def admin_dashboard_data(request):
#     return Response(
#         {
#             "universities": [
#                 {"id": u.id, "name": u.name, "image": u.image.url if u.image else None}
#                 for u in University.objects.all()[:5]
#             ],
#             "courses": [
#                 {"id": c.id, "name": c.name, "university": c.university.name}
#                 for c in Course.objects.select_related("university")[:5]
#             ],
#             "users": [
#                 {"id": user.id, "email": user.email, "is_staff": user.is_staff}
#                 for user in User.objects.order_by("-date_joined")[:5]
#             ],
#         }
#     )


# def login_page(request):
#     return render(request, "website/login.html")
# def login_page(request):
#     if request.method == "POST":
#         email = request.POST.get("email")
#         password = request.POST.get("password")

#         response = requests.post(
#             f"{settings.API_BASE_URL}/api/accounts/login/",
#             json={"email": email, "password": password},
#         )

#         if response.status_code == 200:
#             data = response.json()
#             request.session["access_token"] = data["access"]
#             request.session["refresh_token"] = data["refresh"]
#             return redirect("dashboard")
#         else:
#             return render(
#                 request,
#                 "website/auth/login.html",
#                 {"error": "Invalid email or password"},
#             )

#     return render(request, "website/auth/login.html")


# def register_page(request):
#     return render(request, "website/register.html")


# def register_page(request):
#     if request.method == "POST":
#         username = request.POST.get("username")
#         email = request.POST.get("email")
#         password = request.POST.get("password")

#         print(f"Registering user: {username}, {email}, {password}")

#         response = requests.post(
#             f"{settings.API_BASE_URL}/api/accounts/register/",
#             json={"username": username, "email": email, "password": password},
#         )

#         if response.status_code == 201:
#             request.session["otp_email"] = email
#             return redirect("verify_otp")

#         else:
#             try:
#                 # error = response.json().get("message")
#                 errors = response.json()

#                 if isinstance(errors, dict):
#                     first_key = list(errors.keys())[0]
#                     error = errors[first_key][0]
#                 else:
#                     error = "Registration failed"
#             except:
#                 error = "Registration failed"

#             return render(request, "website/auth/register.html", {"error": error})

#     return render(request, "website/auth/register.html")


# def verify_otp_page(request):
#     email = request.session.get("otp_email")

#     if request.method == "POST":
#         otp = request.POST.get("otp")

#         response = requests.post(
#             f"{settings.API_BASE_URL}/api/accounts/verify-otp/",
#             json={"email": email, "otp": otp},
#         )

#         if response.status_code == 200:
#             return redirect("login")

#         else:
#             return render(
#                 request, "website/auth/verify_otp.html", {"error": "Invalid OTP"}
#             )

#     return render(request, "website/auth/verify_otp.html")


# # def dashboard(request):
# #     return render(request, "website/dashboard.html")
# def dashboard(request):
#     token = request.session.get("access_token")

#     if not token:
#         return redirect("login")

#     return render(request, "website/dashboard.html")


def logout_view(request):
    request.session.flush()
    return redirect("login")


# def universities(request):
#     return render(request, "website/browse/universities.html")


# def courses(request):
#     return render(request, "website/browse/courses.html")
