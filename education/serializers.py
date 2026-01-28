from rest_framework import serializers
from .models import Book, Chapter, Note, Question, Unit, University, Course


class UniversitySerializer(serializers.ModelSerializer):
    course_count = serializers.IntegerField(source="courses.count", read_only=True)
    image = serializers.ImageField()  # DRF automatically uses storage backend

    class Meta:
        model = University
        fields = "id", "name", "description", "image", "course_count", "created_at"
        # fields = "__all__"


class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = "__all__"


class BookSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = "__all__"


class UnitSerializer(serializers.ModelSerializer):
    class Meta:
        model = Unit
        fields = "__all__"


class ChapterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Chapter
        fields = "__all__"


class NoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Note
        fields = "__all__"


class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = "__all__"


class NoteNestedSerializer(serializers.ModelSerializer):
    class Meta:
        model = Note
        fields = ["id", "title", "content"]


class QuestionNestedSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = ["id", "question", "answer"]


class ChapterNestedSerializer(serializers.ModelSerializer):
    notes = NoteNestedSerializer(many=True, read_only=True)
    questions = QuestionNestedSerializer(many=True, read_only=True)

    class Meta:
        model = Chapter
        fields = ["id", "title", "chapter_number", "notes", "questions"]


class UnitNestedSerializer(serializers.ModelSerializer):
    chapters = ChapterNestedSerializer(many=True, read_only=True)

    class Meta:
        model = Unit
        fields = ["id", "name", "chapters"]


class BookDetailSerializer(serializers.ModelSerializer):
    units = UnitNestedSerializer(many=True, read_only=True)

    class Meta:
        model = Book
        fields = ["id", "name", "description", "units"]


# class BookDetailSerializer(serializers.ModelSerializer):
#     units = UnitNestedSerializer(many=True, read_only=True)

#     class Meta:
#         model = Book
#         fields = ["id", "name", "description", "units"]
