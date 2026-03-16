from pathlib import Path

from django.contrib.auth import get_user_model
from django.db.models import Q
from django.http import FileResponse, Http404, HttpResponseForbidden
from rest_framework import filters, viewsets
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework_simplejwt.tokens import AccessToken

from .models import Lesson
from .serializers import LessonSerializer
from .permissions import IsMentorOrReadOnly


class LessonViewSet(viewsets.ModelViewSet):
    serializer_class = LessonSerializer
    permission_classes = [IsAuthenticatedOrReadOnly, IsMentorOrReadOnly]
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["title", "description", "track"]
    ordering_fields = ["created_at", "title"]
    ordering = ["-created_at"]

    def get_queryset(self):
        user = self.request.user
        track = self.request.query_params.get("track")
        if user.is_authenticated and user.is_staff:
            queryset = Lesson.objects.all()
        elif user.is_authenticated and getattr(user, "role", "") == "mentor":
            if self.request.query_params.get("mine") == "1":
                queryset = Lesson.objects.filter(created_by=user)
            else:
                queryset = Lesson.objects.filter(Q(created_by=user) | Q(is_published=True))
        else:
            queryset = Lesson.objects.filter(is_published=True)
        if track:
            queryset = queryset.filter(track=track)
        return queryset.order_by("-created_at")

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


def _resolve_lesson_user(request):
    if getattr(request, "user", None) and request.user.is_authenticated:
        return request.user

    auth_header = request.headers.get("Authorization", "")
    query_token = request.GET.get("token", "")
    raw_token = ""
    if auth_header.startswith("Bearer "):
        raw_token = auth_header.split(" ", 1)[1].strip()
    elif query_token:
        raw_token = query_token.strip()

    if not raw_token:
        return None

    try:
        token = AccessToken(raw_token)
        user_model = get_user_model()
        return user_model.objects.filter(id=token["user_id"]).first()
    except (InvalidToken, TokenError, KeyError):
        return None


def lesson_asset_view(request, pk):
    lesson = Lesson.objects.select_related("created_by").filter(pk=pk).first()
    if not lesson or not lesson.file:
        raise Http404("Lesson asset topilmadi.")

    user = _resolve_lesson_user(request)
    if not user:
        return HttpResponseForbidden("Login required.")

    is_owner = lesson.created_by_id == user.id
    is_mentor = user.is_staff or getattr(user, "role", "") == "mentor"
    if not lesson.is_published and not (is_owner or is_mentor):
        return HttpResponseForbidden("Access denied.")

    if not lesson.is_video_file and not is_mentor:
        return HttpResponseForbidden("Students cannot download this material.")

    response = FileResponse(lesson.file.open("rb"), as_attachment=False, filename=Path(lesson.file.name).name)
    response["Cache-Control"] = "private, no-store"
    response["Content-Disposition"] = f'inline; filename="{Path(lesson.file.name).name}"'
    response["X-Frame-Options"] = "SAMEORIGIN"
    response["Content-Security-Policy"] = "frame-ancestors 'self';"
    return response
