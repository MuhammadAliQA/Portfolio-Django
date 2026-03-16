from django.db.models import Avg, Count, Max, Q
from django.views.generic import TemplateView

from consultations.models import Consultation
from assessments.models import Attempt, Exam
from lessons.models import Lesson
from mentors.models import MentorProfile
from reviews.models import Review


class HomePageView(TemplateView):
    template_name = "index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        mentors = MentorProfile.objects.select_related("user").order_by(
            "-is_featured",
            "-rating",
            "-students_helped",
        )
        featured_mentors = mentors.filter(is_featured=True)[:3]
        if not featured_mentors:
            featured_mentors = mentors[:3]

        total_mentors = mentors.count()
        total_consultations = Consultation.objects.count()
        total_reviews = Review.objects.count()
        avg_rating = Review.objects.aggregate(value=Avg("rating"))["value"] or 4.9

        context.update(
            {
                "featured_mentors": featured_mentors,
                "hero_stats": [
                    {"value": total_mentors or 12, "label": "Faol mentorlar"},
                    {"value": total_consultations or 180, "label": "Sessiyalar"},
                    {"value": f"{avg_rating:.1f}", "label": "O'rtacha baho"},
                ],
                "service_cards": [
                    {
                        "title": "IELTS tayyorgarligi",
                        "description": "Band score diagnostikasi, speaking-writing feedback va individual plan.",
                    },
                    {
                        "title": "SAT strategiyasi",
                        "description": "Target score uchun math-reading roadmap, practice review va time management.",
                    },
                    {
                        "title": "Admission konsulting",
                        "description": "University shortlist, essay review, scholarship strategiyasi va deadline nazorati.",
                    },
                ],
                "journey_steps": [
                    "Bepul diagnostika orqali hozirgi holat va maqsad aniqlanadi.",
                    "Sizga mos mentor va xizmat paketi tanlanadi.",
                    "IELTS, SAT yoki admission uchun individual roadmap tuziladi.",
                    "Jarayon davomida feedback, review va submission nazorati olib boriladi.",
                ],
                "resource_cards": [
                    {
                        "title": "Bepul maslahatlar",
                        "description": "Checklist, webinar va amaliy tavsiyalar orqali keng auditoriyaga yordam.",
                    },
                    {
                        "title": "Premium konsalting",
                        "description": "1-on-1 mentorlik, essay review va to'liq admission support xizmatlari.",
                    },
                    {
                        "title": "Progress monitoring",
                        "description": "Target score va university list bo'yicha muntazam kuzatuv va hisobot.",
                    },
                ],
                "impact_metrics": [
                    {
                        "label": "Admission yo'nalishidagi mentorlar",
                        "value": mentors.filter(offers_admission_support=True).count() or 5,
                    },
                    {
                        "label": "Featured ekspertlar",
                        "value": mentors.filter(is_featured=True).count() or 3,
                    },
                    {
                        "label": "Student reviewlar",
                        "value": total_reviews or 40,
                    },
                ],
            }
        )
        return context


class MentorListPageView(TemplateView):
    template_name = "mentors.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        track = self.request.GET.get("track", "")
        query = self.request.GET.get("q", "")

        mentors = MentorProfile.objects.select_related("user").all()
        if track:
            mentors = mentors.filter(primary_track=track)
        if query:
            mentors = mentors.filter(
                Q(user__first_name__icontains=query)
                | Q(user__last_name__icontains=query)
                | Q(expertise__icontains=query)
                | Q(university_background__icontains=query)
            )

        context.update(
            {
                "mentors": mentors.order_by("-is_featured", "-rating", "price_per_hour"),
                "selected_track": track,
                "search_query": query,
                "track_options": MentorProfile.TRACK_CHOICES,
            }
        )
        return context


class LessonListPageView(TemplateView):
    template_name = "lessons.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        track = self.request.GET.get("track", "")
        lessons = Lesson.objects.filter(is_published=True).select_related("created_by")
        if track:
            lessons = lessons.filter(track=track)
        context.update(
            {
                "lessons": lessons.order_by("-created_at"),
                "selected_track": track,
            }
        )
        return context


class MockTestPageView(TemplateView):
    template_name = "mock_tests.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        exams = Exam.objects.filter(is_published=True).prefetch_related("questions")
        context["exams"] = exams
        context["featured_exam"] = exams.first()
        context["leaderboard"] = (
            Attempt.objects.select_related("user", "exam")
            .values("user__username")
            .annotate(best_score=Max("percentage"), attempts=Count("id"))
            .order_by("-best_score", "-attempts")[:5]
        )
        if self.request.user.is_authenticated:
            context["recent_attempts"] = Attempt.objects.select_related("exam").filter(user=self.request.user)[:4]
            context["track_progress"] = (
                Attempt.objects.filter(user=self.request.user)
                .values("exam__track")
                .annotate(best=Max("percentage"), avg=Avg("percentage"))
                .order_by("exam__track")
            )
        else:
            context["recent_attempts"] = []
            context["track_progress"] = []
        return context
