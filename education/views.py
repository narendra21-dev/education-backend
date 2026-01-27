# Create your views here.

# from rest_framework.views import APIView
# from education.services import create_units_for_course
from django.shortcuts import render
from education.permissions import IsTeacherOrReadOnly
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from .models import Book, Chapter, Course, Note, Question, Unit, University
from .serializers import (
    BookDetailSerializer,
    BookSerializer,
    ChapterSerializer,
    CourseSerializer,
    NoteSerializer,
    QuestionSerializer,
    UnitSerializer,
    UniversitySerializer,
)


class UniversityViewSet(ModelViewSet):
    queryset = University.objects.all()
    serializer_class = UniversitySerializer
    permission_classes = [
        IsAuthenticated,
        IsTeacherOrReadOnly,
    ]  # staff can modify, anyone authenticated can read


class CourseViewSet(ModelViewSet):
    queryset = Course.objects.select_related("university")
    serializer_class = CourseSerializer
    permission_classes = [IsAuthenticated, IsTeacherOrReadOnly]
    filterset_fields = ["university"]


class BookViewSet(ModelViewSet):
    # queryset = Book.objects.select_related("course")
    queryset = Book.objects.prefetch_related(
        "units__chapters__notes", "units__chapters__questions"
    )
    serializer_class = BookSerializer
    permission_classes = [IsAuthenticated, IsTeacherOrReadOnly]
    filterset_fields = ["course"]
    search_fields = ["name"]

    def get_serializer_class(self):
        if self.action == "retrieve":
            return BookDetailSerializer
        return BookSerializer


class UnitViewSet(ModelViewSet):
    queryset = Unit.objects.select_related("book")
    serializer_class = UnitSerializer
    permission_classes = [IsAuthenticated, IsTeacherOrReadOnly]
    filterset_fields = ["book"]


class ChapterViewSet(ModelViewSet):
    queryset = Chapter.objects.select_related("unit")
    serializer_class = ChapterSerializer
    permission_classes = [IsAuthenticated, IsTeacherOrReadOnly]
    filterset_fields = ["unit"]


class NoteViewSet(ModelViewSet):
    queryset = Note.objects.select_related("chapter", "created_by")
    serializer_class = NoteSerializer
    permission_classes = [IsAuthenticated, IsTeacherOrReadOnly]
    filterset_fields = ["chapter"]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class QuestionViewSet(ModelViewSet):
    queryset = Question.objects.select_related("chapter", "created_by")
    serializer_class = QuestionSerializer
    permission_classes = [IsAuthenticated, IsTeacherOrReadOnly]
    filterset_fields = ["chapter"]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


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
