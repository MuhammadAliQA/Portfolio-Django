from django.contrib import admin
from .models import Lesson


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ("title", "track", "is_published", "created_by", "created_at")
    list_filter = ("track", "is_published")
    search_fields = ("title", "description")
