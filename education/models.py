from django.conf import settings
from django.db import models
from cloudinary.models import CloudinaryField
from cloudinary_storage.storage import RawMediaCloudinaryStorage


# Create your models here.
class University(models.Model):
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True)
    image = CloudinaryField("image", folder="universities", blank=True, null=True)
    # image = models.ImageField(upload_to="universities/", null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


# education/models.py
class Course(models.Model):
    CURRICULUM_TYPE = (
        ("semester", "Semester"),
        ("year", "Year"),
    )

    DURATION_UNIT = (
        ("year", "Year"),
        ("semester", "Semester"),
    )

    university = models.ForeignKey(
        "University", on_delete=models.CASCADE, related_name="courses"
    )

    name = models.CharField(max_length=100)

    curriculum_type = models.CharField(
        max_length=10,
        choices=CURRICULUM_TYPE,
        help_text="Academic structure followed by the course",
    )

    duration = models.PositiveIntegerField(
        help_text="Numeric duration (e.g. 2, 3, 4, 6, 8)",
    )

    duration_unit = models.CharField(
        max_length=10,
        choices=DURATION_UNIT,
        help_text="Year or Semester",
    )

    def __str__(self):
        return f"{self.name} ({self.duration} {self.duration_unit})"


class AcademicPeriod(models.Model):
    PERIOD_TYPE = (
        ("semester", "Semester"),
        ("year", "Year"),
    )

    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="periods")
    period_type = models.CharField(max_length=10, choices=PERIOD_TYPE)
    number = models.PositiveIntegerField()
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order"]
        unique_together = ("course", "number", "period_type")

    def __str__(self):
        return f"{self.period_type.capitalize()} {self.number}"


class Book(models.Model):
    # course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="books")

    # period = models.ForeignKey(
    #     AcademicPeriod, on_delete=models.CASCADE, related_name="books"
    # )
    period = models.ForeignKey(
        AcademicPeriod,
        on_delete=models.CASCADE,
        related_name="books",
    )

    name = models.CharField(max_length=150)
    description = models.TextField(blank=True)
    cover_image = CloudinaryField(
        "image", folder="books", blank=True, null=True
    )  # changed
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("period", "name")
        # unique_together = ("course", "name")
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} - {self.period}"
        # return f"{self.name} - {self.course.name}"


class Unit(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name="units")
    name = models.CharField(max_length=150)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("book", "name")
        ordering = ["name"]

    def __str__(self):
        return self.name


class Chapter(models.Model):
    unit = models.ForeignKey(Unit, on_delete=models.CASCADE, related_name="chapters")
    title = models.CharField(max_length=200)
    chapter_number = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("unit", "chapter_number")
        ordering = ["chapter_number"]

    def __str__(self):
        return f"Chapter {self.chapter_number}: {self.title}"


class Note(models.Model):
    chapter = models.ForeignKey(Chapter, on_delete=models.CASCADE, related_name="notes")
    title = models.CharField(max_length=200)
    content = models.TextField()
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="notes",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


# class NoteImage(models.Model):

#     note = models.ForeignKey(
#         Note,
#         on_delete=models.CASCADE,
#         related_name="images"
#     )

#     image = CloudinaryField(
#         "image",
#         folder="notes"
#     )

#     uploaded_at = models.DateTimeField(auto_now_add=True)

#     def __str__(self):
#         return f"Image for {self.note.title}"


# ✅ PUT HERE
class NoteImage(models.Model):
    note = models.ForeignKey(Note, on_delete=models.CASCADE, related_name="images")

    image = CloudinaryField("image", folder="notes")

    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Image for {self.note.title}"


class Question(models.Model):
    chapter = models.ForeignKey(
        Chapter, on_delete=models.CASCADE, related_name="questions"
    )
    question = models.TextField()
    answer = models.TextField(blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="questions",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.question[:50]


class Paper(models.Model):
    chapter = models.ForeignKey(
        Chapter, on_delete=models.CASCADE, related_name="papers"
    )

    title = models.CharField(max_length=255)

    # pdf = models.FileField(upload_to="papers/")

    pdf = models.FileField(upload_to="papers/", storage=RawMediaCloudinaryStorage())


    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
