from django.contrib import admin

from .models import Answer, Attempt, Choice, Exam, Question


class ChoiceInline(admin.TabularInline):
    model = Choice
    extra = 2


class QuestionInline(admin.StackedInline):
    model = Question
    extra = 1


@admin.register(Exam)
class ExamAdmin(admin.ModelAdmin):
    list_display = ("title", "track", "section", "duration_minutes", "is_published")
    list_filter = ("track", "is_published")
    search_fields = ("title", "section", "description")


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ("exam", "order", "points")
    inlines = [ChoiceInline]


@admin.register(Attempt)
class AttemptAdmin(admin.ModelAdmin):
    list_display = ("user", "exam", "score", "max_score", "percentage", "created_at")
    search_fields = ("user__username", "exam__title")


@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    list_display = ("attempt", "question", "selected_choice", "is_correct")
