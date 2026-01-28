from django.contrib import admin

from .models import Book, Chapter, Course, Note, Question, Unit, University
from django.utils.html import format_html

# Register your models here.


# @admin.register(University)
# class UniversityAdmin(admin.ModelAdmin):
#     list_display = ("id", "name", "description", "image", "created_at")
#     search_fields = ["name", "description"]
#     list_filter = ["created_at"]


@admin.register(University)
class UniversityAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "preview_image")

    def preview_image(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" width="60" height="60" style="border-radius:6px;" />',
                obj.image.url,
            )
        return "No Image"

    preview_image.short_description = "Image"


# -----------------------
# Course Admin
# -----------------------
@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "name",
        "university",
        "curriculum_type",
        "duration",
        "duration_unit",
    ]
    search_fields = ["name", "university__name"]
    list_filter = ["curriculum_type", "duration_unit", "university"]


# -----------------------
# Book Admin
# -----------------------
@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ["id", "name", "course", "created_at"]
    search_fields = ["name", "course__name"]
    list_filter = ["course"]


# -----------------------
# Unit Admin
# -----------------------
@admin.register(Unit)
class UnitAdmin(admin.ModelAdmin):
    list_display = ["id", "name", "book", "created_at"]
    search_fields = ["name", "book__name"]
    list_filter = ["book"]


# -----------------------
# Chapter Admin
# -----------------------
@admin.register(Chapter)
class ChapterAdmin(admin.ModelAdmin):
    list_display = ["id", "title", "chapter_number", "unit", "created_at"]
    search_fields = ["title", "unit__name"]
    list_filter = ["unit"]


# -----------------------
# Note Admin
# -----------------------
@admin.register(Note)
class NoteAdmin(admin.ModelAdmin):
    list_display = ["id", "title", "chapter", "created_by", "created_at"]
    search_fields = ["title", "chapter__title", "created_by__email"]
    list_filter = ["chapter"]


# -----------------------
# Question Admin
# -----------------------
@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ["id", "question", "chapter", "created_by", "created_at"]
    search_fields = ["question", "chapter__title", "created_by__email"]
    list_filter = ["chapter"]


# @admin.register(Course)
# class CourseAdmin(admin.ModelAdmin):
#     list_display = (
#         "id",
#         "university",
#         "name",
#         "curriculum_type",
#         "duration",
#         "duration_unit",
#     )
#     search_fields = ("name",)
#     list_filter = (
#         "university",
#         "curriculum_type",
#     )


# @admin.register(Book)
# class BookAdmin(admin.ModelAdmin):
#     list_display = ("id", "name", "course", "created_at")
#     list_filter = ("course",)
#     search_fields = ("name",)


# @admin.register(Unit)
# class UnitAdmin(admin.ModelAdmin):
#     list_display = ("name", "book", "created_at")
#     list_filter = ("book",)
#     search_fields = ("name",)


# @admin.register(Chapter)
# class ChapterAdmin(admin.ModelAdmin):
#     list_display = ("id", "title", "chapter_number", "unit", "created_at")
#     list_filter = ("unit",)
#     search_fields = ("title",)


# @admin.register(Note)
# class NoteAdmin(admin.ModelAdmin):
#     list_display = ("id", "title", "chapter", "created_by", "created_at")
#     list_filter = ("chapter",)
#     search_fields = ("title",)


# @admin.register(Question)
# class QuestionAdmin(admin.ModelAdmin):
#     list_display = ("question", "chapter", "created_by", "created_at")
#     list_filter = ("chapter",)
#     search_fields = ("question",)
