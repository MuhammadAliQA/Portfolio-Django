from rest_framework.routers import DefaultRouter
from .views import MentorViewSet

app_name = 'mentors'
router = DefaultRouter()
router.register(r'', MentorViewSet, basename='mentor')
urlpatterns = router.urls