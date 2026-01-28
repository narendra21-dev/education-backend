from django.contrib import admin

from .models import Book, Chapter, Course, Note, Question, Unit, University

# Register your models here.


@admin.register(University)
class UniversityAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "description", "image", "course_count", "created_at")
    search_fields = ("name",)


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "university",
        "name",
        "curriculum_type",
        "duration",
        "duration_unit",
    )
    search_fields = ("name",)
    list_filter = (
        "university",
        "curriculum_type",
    )


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "course", "created_at")
    list_filter = ("course",)
    search_fields = ("name",)


@admin.register(Unit)
class UnitAdmin(admin.ModelAdmin):
    list_display = ("name", "book", "created_at")
    list_filter = ("book",)
    search_fields = ("name",)


@admin.register(Chapter)
class ChapterAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "chapter_number", "unit", "created_at")
    list_filter = ("unit",)
    search_fields = ("title",)


@admin.register(Note)
class NoteAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "chapter", "created_by", "created_at")
    list_filter = ("chapter",)
    search_fields = ("title",)


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ("question", "chapter", "created_by", "created_at")
    list_filter = ("chapter",)
    search_fields = ("question",)
