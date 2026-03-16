from decimal import Decimal

from django.db import transaction
from django.db.models import Count, Prefetch
from rest_framework import mixins, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Answer, Attempt, Choice, Exam, Question
from .serializers import (
    AttemptResultSerializer,
    AttemptSerializer,
    ExamDetailSerializer,
    ExamListSerializer,
    ExamSubmissionSerializer,
)


class ExamViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        return (
            Exam.objects.filter(is_published=True)
            .annotate(questions_count=Count("questions"))
            .prefetch_related(Prefetch("questions", queryset=Question.objects.prefetch_related("choices")))
            .order_by("track", "title")
        )

    def get_serializer_class(self):
        if self.action == "retrieve":
            return ExamDetailSerializer
        return ExamListSerializer

    @action(detail=True, methods=["post"], permission_classes=[permissions.IsAuthenticated])
    def submit(self, request, pk=None):
        exam = self.get_object()
        serializer = ExamSubmissionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        answers_payload = serializer.validated_data["answers"]
        questions = {question.id: question for question in exam.questions.all()}
        choices = {
            choice.id: choice
            for question in questions.values()
            for choice in question.choices.all()
        }

        score = 0
        max_score = sum(question.points for question in questions.values())

        with transaction.atomic():
            attempt = Attempt.objects.create(
                user=request.user,
                exam=exam,
                max_score=max_score,
            )

            for item in answers_payload:
                question = questions.get(item["question"])
                choice = choices.get(item["choice"])
                if not question or not choice or choice.question_id != question.id:
                    transaction.set_rollback(True)
                    return Response(
                        {"error": "Savol yoki variant noto'g'ri yuborildi."},
                        status=status.HTTP_400_BAD_REQUEST,
                    )

                is_correct = choice.is_correct
                if is_correct:
                    score += question.points

                Answer.objects.create(
                    attempt=attempt,
                    question=question,
                    selected_choice=choice,
                    is_correct=is_correct,
                )

            attempt.score = score
            attempt.percentage = Decimal("0.00") if max_score == 0 else round((Decimal(score) / Decimal(max_score)) * 100, 2)
            attempt.save(update_fields=["score", "percentage"])

        return Response(AttemptResultSerializer(attempt).data, status=status.HTTP_201_CREATED)


class AttemptViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    serializer_class = AttemptSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Attempt.objects.select_related("exam").filter(user=self.request.user)
