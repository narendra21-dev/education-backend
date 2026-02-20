from rest_framework import serializers
from .models import (
    AcademicPeriod,
    Book,
    Chapter,
    Note,
    NoteImage,
    Paper,
    Question,
    Unit,
    University,
    Course,
)


class UniversitySerializer(serializers.ModelSerializer):
    course_count = serializers.IntegerField(source="courses.count", read_only=True)
    # image = serializers.SerializerMethodField()
    image = serializers.ImageField(required=False, allow_null=True)
    image_url = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = University
        fields = "__all__"

    # def get_image(self, obj):
    #     if obj.image:
    #         # Cloudinary returns full URL when using django-cloudinary-storage
    #         return obj.image.url
    #     return None

    def get_image_url(self, obj):
        return obj.image.url if obj.image else None


class AcademicPeriodSerializer(serializers.ModelSerializer):
    class Meta:
        model = AcademicPeriod
        fields = "__all__"


class CourseSerializer(serializers.ModelSerializer):
    periods = AcademicPeriodSerializer(many=True, read_only=True)

    class Meta:
        model = Course
        fields = "__all__"


class BookSerializer(serializers.ModelSerializer):
    cover_url = serializers.SerializerMethodField()

    class Meta:
        model = Book
        fields = "__all__"
        read_only_fields = ["cover_url"]

    def get_cover_url(self, obj):
        if obj.cover_image:
            return obj.cover_image.url
        return None


# class UnitSerializer(serializers.ModelSerializer):
#     chapter_count = serializers.IntegerField(source="chapters.count", read_only=True)
#     chapter_preview = serializers.SerializerMethodField()

#     class Meta:
#         model = Unit
#         fields = "__all__"


# class UnitSerializer(serializers.ModelSerializer):
#     chapter_count = serializers.IntegerField(source="chapters.count", read_only=True)

#     chapter_preview = serializers.SerializerMethodField()

#     class Meta:
#         model = Unit

#         fields = [
#             "id",
#             "book",
#             "name",
#             "created_at",
#             "chapter_count",
#             "chapter_preview",
#         ]

#     def get_chapter_preview(self, obj):
#         chapters = obj.chapters.all()[:5]

#         return [{"id": chapter.id, "name": chapter.name} for chapter in chapters]


class UnitSerializer(serializers.ModelSerializer):
    chapter_count = serializers.IntegerField(source="chapters.count", read_only=True)

    chapter_preview = serializers.SerializerMethodField()

    class Meta:
        model = Unit
        fields = "__all__"

    def get_chapter_preview(self, obj):
        chapters = obj.chapters.all()[:5]

        return [
            {
                "id": chapter.id,
                "title": chapter.title,
                "chapter_number": chapter.chapter_number,
            }
            for chapter in chapters
        ]


class ChapterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Chapter
        fields = "__all__"


# class NoteSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Note
#         fields = "__all__"


# Image Serializer


# class NoteImageSerializer(serializers.ModelSerializer):
#     image_url = serializers.SerializerMethodField()

#     class Meta:
#         model = NoteImage

#         fields = ["id", "image", "image_url"]

#     def get_image_url(self, obj):
#         if obj.image:
#             return obj.image.url

#         return None


# Note Serializer


# class NoteSerializer(serializers.ModelSerializer):
#     images = NoteImageSerializer(many=True, read_only=True)

#     class Meta:
#         model = Note

#         fields = [
#             "id",
#             "chapter",
#             "title",
#             "content",
#             "created_by",
#             "created_at",
#             "images",
#         ]

#         read_only_fields = ["created_by", "created_at"]


# class NoteSerializer(serializers.ModelSerializer):
#     images = NoteImageSerializer(many=True, read_only=True)

#     class Meta:
#         model = Note

#         fields = "__all__"


class NoteImageSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    class Meta:
        model = NoteImage
        fields = ["id", "image"]

    def get_image(self, obj):
        if obj.image:
            return obj.image.url  # IMPORTANT

        return None


class NoteSerializer(serializers.ModelSerializer):
    images = NoteImageSerializer(many=True, read_only=True)

    class Meta:
        model = Note

        fields = [
            "id",
            "title",
            "content",
            "chapter",
            "created_at",
            "created_by",
            "images",
        ]


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


# class PaperSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Paper


#         fields = "__all__"
# class PaperSerializer(serializers.ModelSerializer):
#     pdf = serializers.SerializerMethodField()

#     class Meta:
#         model = Paper

#         fields = "__all__"

#     def get_pdf(self, obj):
#         request = self.context.get("request")

#         if obj.pdf:
#             return request.build_absolute_uri(obj.pdf.url)

#         return None


class PaperSerializer(serializers.ModelSerializer):
    pdf_url = serializers.SerializerMethodField()

    class Meta:
        model = Paper
        fields = "__all__"

    def get_pdf_url(self, obj):
        if obj.pdf:
            return obj.pdf.url
        return None


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
