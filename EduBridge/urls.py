from django.contrib import admin
from django.contrib.messages import api
from django.urls import path, include
from django.views.generic import TemplateView
from django.conf import settings
from django.conf.urls.static import static

from .views import HomePageView, LessonListPageView, MentorListPageView, MockTestPageView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', HomePageView.as_view(), name='home'),
    path('mentors/', MentorListPageView.as_view(), name='mentors'),
    path('lessons/', LessonListPageView.as_view(), name='lessons'),
    path('mock-tests/', MockTestPageView.as_view(), name='mock-tests'),
    path('student-dashboard/', TemplateView.as_view(template_name='students_dashboard.html'), name='student-dashboard'),
    path('mentor-dashboard/',  TemplateView.as_view(template_name='mentors_dashboard.html'),  name='mentor-dashboard'),
    path('login/',    TemplateView.as_view(template_name='login.html'),    name='login'),
    path('register/', TemplateView.as_view(template_name='register.html'), name='register'),
    path('faq/', TemplateView.as_view(template_name='faq.html'), name='faq'),
    path('information/', TemplateView.as_view(template_name='information.html'), name='information'),
    path('sitemap/', TemplateView.as_view(template_name='sitemap.html'), name='sitemap'),
    path('api/users/', include('users.urls')),
    path('api/mentors/', include('mentors.urls')),
    path('api/consultations/', include('consultations.urls')),
    path('api/payments/', include('payments.urls')),
    path('api/lessons/', include('lessons.urls')),
    path('api/reviews/', include('reviews.urls')),
    path('api/assessments/', include('assessments.urls')),
    ]
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])
    urlpatterns += static(settings.MEDIA_URL,  document_root=settings.MEDIA_ROOT)
