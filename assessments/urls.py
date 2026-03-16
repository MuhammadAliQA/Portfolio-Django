from rest_framework.routers import DefaultRouter

from .views import AttemptViewSet, ExamViewSet


router = DefaultRouter()
router.register(r"exams", ExamViewSet, basename="assessment-exam")
router.register(r"attempts", AttemptViewSet, basename="assessment-attempt")

urlpatterns = router.urls
