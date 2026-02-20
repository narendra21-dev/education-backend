from django.urls import path
from . import views
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    # path("", views.home, name="home"),
    # path("login/", views.login_view, name="login"),
    # path("register/", views.register_view, name="register"),
    # path("dashboard/", views.dashboard, name="dashboard"),
    # path("logout/", views.logout_view, name="logout"),
    # path("universities/", views.universities, name="universities"),
    # path("courses/", views.courses, name="courses"),
    path("", views.home, name="home"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("logout/", views.logout_view, name="logout"),
    # Auth
    path("login/", views.login_view, name="login"),
    path("register/", views.register_view, name="register"),
    path("verify-otp/", views.verify_otp_view, name="verify_otp"),
    path("forgot-password/", views.forgot_password, name="forgot_password"),
    path("forgot-password/verify/", views.verify_forgot_otp),
    path("forgot-password/reset/", views.reset_password),
    # Browse
    path("universities/", views.universities, name="universities"),
    path("courses/", views.courses, name="courses"),
    path("periods/", views.periods, name="periods"),
    path("books/", views.books, name="books"),
    path("units/", views.units, name="units"),
    path("chapters/", views.chapters, name="chapters"),
    path("chapter-details/", views.chapter_details, name="chapter-details"),
    path("questions/", views.questions_page, name="questions-page"),
    path("papers/", views.papers_page, name="papers-page"),
    # path("papers/<id>/preview/", views.pdf_preview),
    path("papers/<int:paper_id>/preview/", views.pdf_preview, name="paper_preview"),
    # path("papers/view/<int:pk>/", views.paper_preview, name="paper_preview"),
    path("notes/", views.notes_page, name="notes-page"),
    path("note_detail/", views.note_detail, name="note_detail"),
    # path("delete-image/<int:id>/",DeleteImageView.as_view()),
]


urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])
