from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import LessonViewSet, lesson_asset_view


router = DefaultRouter()
router.register(r"", LessonViewSet, basename="lesson")

urlpatterns = [
    path("<int:pk>/asset/", lesson_asset_view, name="lesson-asset"),
]

urlpatterns += router.urls
