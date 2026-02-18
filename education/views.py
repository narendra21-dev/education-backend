# Create your views here.

# from rest_framework.views import APIView
# from education.services import create_units_for_course
from django.shortcuts import render
from education.permissions import IsTeacherOrReadOnly
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.permissions import IsAdminUser
from rest_framework.permissions import AllowAny
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.filters import SearchFilter
from rest_framework import filters
from django.db import transaction
from django.db.models import Max
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.views import APIView
from rest_framework.decorators import action
from .models import (
    AcademicPeriod,
    Book,
    Chapter,
    Course,
    Note,
    NoteImage,
    Paper,
    Question,
    Unit,
    University,
)
from .serializers import (
    AcademicPeriodSerializer,
    BookDetailSerializer,
    BookSerializer,
    ChapterSerializer,
    CourseSerializer,
    NoteImageSerializer,
    NoteSerializer,
    PaperSerializer,
    QuestionSerializer,
    UnitSerializer,
    UniversitySerializer,
)


class UniversityViewSet(ModelViewSet):
    # queryset = University.objects.all()
    queryset = University.objects.all().order_by("-id")  # FIX pagination warning
    serializer_class = UniversitySerializer
    permission_classes = [
        IsAuthenticated,
        IsTeacherOrReadOnly,
    ]  # staff can modify, anyone authenticated can read
    filter_backends = [SearchFilter]
    parser_classes = [MultiPartParser, FormParser]  # 🔥 THIS LINE

    filterset_fields = ["name"]
    search_fields = ["name"]

    def create(self, request, *args, **kwargs):
        print("DATA:", request.data)
        print("FILES:", request.FILES)  # 👈 DEBUG
        return super().create(request, *args, **kwargs)

    def get_permissions(self):
        if self.request.method in ["POST", "PUT", "PATCH", "DELETE"]:
            return [IsAdminUser()]
        return [IsAuthenticated()]


# class CourseViewSet(ModelViewSet):
#     # queryset = Course.objects.select_related("university")
#     queryset = Course.objects.select_related("university").order_by("-id")
#     serializer_class = CourseSerializer
#     permission_classes = [IsAuthenticated, IsTeacherOrReadOnly]
#     filterset_fields = ["university"]
#     filter_backends = [
#         DjangoFilterBackend,
#         filters.SearchFilter,
#         filters.OrderingFilter,
#     ]
#     search_fields = ["name"]


class CourseViewSet(ModelViewSet):
    queryset = Course.objects.select_related("university")
    serializer_class = CourseSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ["university"]

    @transaction.atomic
    def perform_create(self, serializer):
        course = serializer.save()


class AcademicPeriodViewSet(ModelViewSet):
    queryset = AcademicPeriod.objects.select_related("course")
    serializer_class = AcademicPeriodSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ["course"]

    def perform_create(self, serializer):
        course = serializer.validated_data["course"]
        max_order = (
            AcademicPeriod.objects.filter(course=course).aggregate(Max("order"))[
                "order__max"
            ]
            or 0
        )

        serializer.save(order=max_order + 1)


class BookViewSet(ModelViewSet):
    # queryset = Book.objects.select_related("course")
    # queryset = Book.objects.prefetch_related(
    #     "units__chapters__notes", "units__chapters__questions"
    # )
    queryset = Book.objects.select_related(
        "period", "period__course", "period__course__university"
    ).prefetch_related("units__chapters__notes", "units__chapters__questions")
    serializer_class = BookSerializer
    permission_classes = [IsAuthenticated, IsTeacherOrReadOnly]
    # permission_classes = [IsAuthenticated]
    # filterset_fields = ["course"]
    filterset_fields = ["period", "period__course"]
    search_fields = ["name"]

    def get_serializer_class(self):
        if self.action == "retrieve":
            return BookDetailSerializer
        return BookSerializer

    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
            return [AllowAny()]
        return [IsAdminUser()]


# class UnitViewSet(ModelViewSet):
#     queryset = Unit.objects.select_related("book")
#     serializer_class = UnitSerializer
#     permission_classes = [IsAuthenticated, IsTeacherOrReadOnly]
#     filterset_fields = ["book"]


class UnitViewSet(ModelViewSet):
    queryset = Unit.objects.select_related("book").prefetch_related("chapters")

    serializer_class = UnitSerializer

    permission_classes = [IsAuthenticated, IsTeacherOrReadOnly]

    filterset_fields = ["book"]


# class ChapterViewSet(ModelViewSet):
#     queryset = Chapter.objects.select_related("unit")
#     serializer_class = ChapterSerializer
#     permission_classes = [IsAuthenticated, IsTeacherOrReadOnly]
#     filterset_fields = ["unit"]


# class ChapterViewSet(ModelViewSet):
#     queryset = Chapter.objects.select_related("unit")

#     serializer_class = ChapterSerializer

#     permission_classes = [IsAuthenticated]

#     def get_queryset(self):
#         queryset = super().get_queryset()

#         unit_id = self.request.query_params.get("unit")

#         if unit_id:
#             queryset = queryset.filter(unit_id=unit_id)

#         return queryset


class ChapterViewSet(ModelViewSet):
    queryset = Chapter.objects.select_related("unit")

    serializer_class = ChapterSerializer

    permission_classes = [IsAuthenticated, IsTeacherOrReadOnly]

    def get_queryset(self):
        queryset = super().get_queryset()

        unit_id = self.request.query_params.get("unit")

        if unit_id:
            queryset = queryset.filter(unit_id=unit_id)

        return queryset

    @action(detail=True, methods=["get"], url_path="dashboard")
    def dashboard(self, request, pk=None):
        chapter = self.get_object()

        return Response(
            {
                "id": chapter.id,
                "title": chapter.title,
                "questions_count": chapter.questions.count(),
                "notes_count": chapter.notes.count(),
                "papers_count": chapter.papers.count(),
            }
        )

    # @action(detail=True, methods=["get"], url_path="dashboard")
    # def dashboard(self, request, pk=None):
    #     chapter = self.get_object()

    #     return Response(
    #         {
    #             "id": chapter.id,
    #             "title": chapter.title,
    #             "questions_count": chapter.questions.count(),
    #             "notes_count": chapter.notes.count(),
    #         }
    #     )


# class NoteViewSet(ModelViewSet):
#     queryset = Note.objects.select_related("chapter", "created_by")
#     serializer_class = NoteSerializer
#     permission_classes = [IsAuthenticated, IsTeacherOrReadOnly]
#     filterset_fields = ["chapter"]


#     def perform_create(self, serializer):
#         serializer.save(created_by=self.request.user)


# class NoteViewSet(ModelViewSet):
#     queryset = Note.objects.select_related("chapter", "created_by").prefetch_related(
#         "images"
#     )

#     serializer_class = NoteSerializer

#     # permission_classes = [IsAuthenticatedOrReadOnly]
#     permission_classes = [IsAuthenticated, IsTeacherOrReadOnly]

#     filterset_fields = ["chapter"]

#     search_fields = ["title", "content"]

#     def perform_create(self, serializer):
#         serializer.save(created_by=self.request.user)


# class NoteViewSet(ModelViewSet):
#     serializer_class = NoteSerializer
#     permission_classes = [IsAuthenticated]

#     def get_queryset(self):
#         chapter = self.request.query_params.get("chapter")

#         queryset = Note.objects.select_related("chapter", "created_by")

#         if chapter:
#             queryset = queryset.filter(chapter=chapter)

#         return queryset.order_by("-created_at")

#     def perform_create(self, serializer):
#         serializer.save(created_by=self.request.user)


# class NoteViewSet(ModelViewSet):
#     queryset = Note.objects.prefetch_related("images")

#     serializer_class = NoteSerializer

#     permission_classes = [IsAuthenticated, IsTeacherOrReadOnly]

#     def perform_create(self, serializer):
#         serializer.save(created_by=self.request.user)


# class NoteViewSet(ModelViewSet):
#     queryset = Note.objects.prefetch_related("images")

#     serializer_class = NoteSerializer

#     permission_classes = [IsAuthenticated]

#     parser_classes = [MultiPartParser, FormParser]

#     def perform_create(self, serializer):
#         note = serializer.save(created_by=self.request.user)

#         print("FILES:", self.request.FILES)

#         images = self.request.FILES.getlist("images")

#         print("IMAGE LIST:", images)


#         for image in images:
#             NoteImage.objects.create(note=note, image=image)
# class NoteViewSet(ModelViewSet):
#     queryset = Note.objects.prefetch_related("images")

#     serializer_class = NoteSerializer

#     permission_classes = [IsAuthenticated]

#     parser_classes = [MultiPartParser, FormParser]

#     def get_queryset(self):
#         chapter = self.request.query_params.get("chapter")

#         if chapter:
#             return self.queryset.filter(chapter=chapter)

#         return self.queryset

#     def perform_create(self, serializer):
#         note = serializer.save(created_by=self.request.user)

#         images = self.request.FILES.getlist("images")

#         for image in images:
#             NoteImage.objects.create(note=note, image=image)


# class NoteViewSet(ModelViewSet):
#     queryset = Note.objects.all().prefetch_related("images")

#     serializer_class = NoteSerializer

#     parser_classes = [MultiPartParser, FormParser]

#     def perform_create(self, serializer):
#         note = serializer.save(created_by=self.request.user)

#         images = self.request.FILES.getlist("images")

#         for image in images:
#             NoteImage.objects.create(note=note, image=image)


class NoteViewSet(ModelViewSet):
    queryset = Note.objects.all().prefetch_related("images")
    serializer_class = NoteSerializer  # Add this line

    parser_classes = [MultiPartParser, FormParser]

    def perform_create(self, serializer):
        note = serializer.save(created_by=self.request.user)

        for image in self.request.FILES.getlist("images"):
            NoteImage.objects.create(note=note, image=image)

    def perform_update(self, serializer):
        note = serializer.save()

        images = self.request.FILES.getlist("images")

        if images:
            for image in images:
                NoteImage.objects.create(note=note, image=image)


class NoteImageViewSet(ModelViewSet):
    queryset = NoteImage.objects.all()

    serializer_class = NoteImageSerializer

    permission_classes = [IsAuthenticated]


class DeleteImageView(APIView):
    permission_classes = [IsAuthenticated, IsTeacherOrReadOnly]

    def delete(self, request, id):
        image = NoteImage.objects.get(id=id)

        image.delete()

        return Response({"message": "deleted"})


class QuestionViewSet(ModelViewSet):
    queryset = Question.objects.select_related("chapter", "created_by")
    serializer_class = QuestionSerializer
    permission_classes = [IsAuthenticated, IsTeacherOrReadOnly]
    filterset_fields = ["chapter"]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class PaperViewSet(ModelViewSet):
    queryset = Paper.objects.select_related("chapter")

    serializer_class = PaperSerializer

    permission_classes = [IsAuthenticated, IsTeacherOrReadOnly]

    filterset_fields = ["chapter"]

    def get_queryset(self):
        chapter = self.request.query_params.get("chapter")

        if chapter:
            return Paper.objects.filter(chapter=chapter)

        return Paper.objects.all()


def test_static_media(request):
    # Example media image URL (from DB or static path)
    media_image = "/media/universities/iii_GyXZ7Gt.png"
    return render(request, "test_static_media.html", {"media_image": media_image})


# # Course → filter by university
# class CourseViewSet(ModelViewSet):
#     queryset = Course.objects.select_related("university")
#     serializer_class = CourseSerializer
#     permission_classes = [IsAuthenticated, IsTeacherOrReadOnly]
#     filterset_fields = ["university"]


# # Book → filter by course
# class BookViewSet(ModelViewSet):
#     queryset = Book.objects.select_related("course")
#     serializer_class = BookSerializer
#     permission_classes = [IsAuthenticated, IsTeacherOrReadOnly]
#     filterset_fields = ["course"]


# # Unit → filter by book
# class UnitViewSet(ModelViewSet):
#     queryset = Unit.objects.select_related("book")
#     serializer_class = UnitSerializer
#     permission_classes = [IsAuthenticated, IsTeacherOrReadOnly]
#     filterset_fields = ["book"]


# # Chapter → filter by unit
# class ChapterViewSet(ModelViewSet):
#     queryset = Chapter.objects.select_related("unit")
#     serializer_class = ChapterSerializer
#     permission_classes = [IsAuthenticated, IsTeacherOrReadOnly]
#     filterset_fields = ["unit"]


# # Notes → filter by chapter
# class NoteViewSet(ModelViewSet):
#     queryset = Note.objects.select_related("chapter", "created_by")
#     serializer_class = NoteSerializer
#     permission_classes = [IsAuthenticated, IsTeacherOrReadOnly]
#     filterset_fields = ["chapter"]

#     def perform_create(self, serializer):
#         serializer.save(created_by=self.request.user)


# # Questions → filter by chapter
# class QuestionViewSet(ModelViewSet):
#     queryset = Question.objects.select_related("chapter", "created_by")
#     serializer_class = QuestionSerializer
#     permission_classes = [IsAuthenticated, IsTeacherOrReadOnly]
#     filterset_fields = ["chapter"]

#     def perform_create(self, serializer):
#         serializer.save(created_by=self.request.user)
