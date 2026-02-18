from django.urls import path
from .views import (
    AcademicPeriodViewSet,
    BookViewSet,
    ChapterViewSet,
    CourseViewSet,
    DeleteImageView,
    NoteImageViewSet,
    NoteViewSet,
    PaperViewSet,
    QuestionViewSet,
    UnitViewSet,
    UniversityViewSet,
    test_static_media,
)
from rest_framework.routers import DefaultRouter


# urlpatterns = [
#     path("universities/", UniversityListCreateView.as_view(), name="universities"),
# ]

router = DefaultRouter()
router.register("universities", UniversityViewSet, basename="university")
router.register("courses", CourseViewSet)
router.register("periods", AcademicPeriodViewSet)
router.register("books", BookViewSet)
router.register("units", UnitViewSet)
router.register("chapters", ChapterViewSet)
router.register("notes", NoteViewSet)
router.register("note-images", NoteImageViewSet)

router.register("questions", QuestionViewSet)
router.register("papers", PaperViewSet)


urlpatterns = router.urls

urlpatterns += [
    path("test-static-media/", test_static_media, name="test-static-media"),
    path("delete-image/<int:id>/", DeleteImageView.as_view()),
]
