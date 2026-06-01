"""Django models for the course management system."""
from django.db import models
from django.contrib.auth.models import User


class Course(models.Model):
    """Represents a course in the learning management system."""

    name = models.CharField("Назва курсу", max_length=100)
    description = models.TextField("Опис", default='-')
    price = models.IntegerField("Ціна", default=10000)
    image = models.ImageField("Зображення", null=True, blank=True)
    teacher = models.ForeignKey(User, verbose_name="Викладач", on_delete=models.RESTRICT)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Курс"
        verbose_name_plural = "Курси"

    def __str__(self):
        return f"{self.name} : {self.price}"


ROLE_OPTIONS = [('std', "Студент"), ('ast', "Асистент")]

class CourseMember(models.Model):
    """Represents a member of a course (student or assistant)."""

    course_id = models.ForeignKey(Course, verbose_name="Курс", on_delete=models.RESTRICT)
    user_id = models.ForeignKey(User, verbose_name="Студент", on_delete=models.RESTRICT)
    roles = models.CharField("Роль", max_length=3, choices=ROLE_OPTIONS, default='std')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Запис на курс"
        verbose_name_plural = "Записи на курси"

    def __str__(self):
        return f"{self.course_id} : {self.user_id}"


class CourseContent(models.Model):
    """Represents course content such as lessons, modules, or materials."""

    name = models.CharField("Назва контенту", max_length=200)
    description = models.TextField("Опис", default='-')
    video_url = models.CharField("URL відео", max_length=200, null=True, blank=True)
    file_attachment = models.FileField("Файл", null=True, blank=True)
    course_id = models.ForeignKey(Course, verbose_name="Курс", on_delete=models.RESTRICT)
    parent_id = models.ForeignKey("self", verbose_name="Батьківський елемент",
                                  on_delete=models.RESTRICT, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Контент курсу"
        verbose_name_plural = "Контент курсів"

    def __str__(self):
        return f"[{self.course_id}] {self.name}"


class Comment(models.Model):
    """Represents a comment on course content."""

    content_id = models.ForeignKey(CourseContent, verbose_name="Контент", on_delete=models.CASCADE)
    user_id = models.ForeignKey(User, verbose_name="Користувач", on_delete=models.CASCADE)
    comment = models.TextField("Коментар")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Коментар"
        verbose_name_plural = "Коментарі"

    def __str__(self):
        return f"Коментар: {self.content_id.name} - {self.user_id}"


class CourseLike(models.Model):
    """Represents a user liking a course."""

    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="likes")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="liked_courses")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["course", "user"], name="unique_course_like")
        ]
        verbose_name = "Вподобання курсу"
        verbose_name_plural = "Вподобання курсів"

    def __str__(self):
        return f"{self.user.username} вподобав {self.course.name}"