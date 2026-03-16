from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from .models import MentorProfile, MentorAvailability, FavoriteMentor
from .serializers import MentorSerializer, MentorAvailabilitySerializer


class MentorViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Mentorlar ro'yxati — faqat o'qish (ReadOnly).
    Admin panelda yaratiladi, API orqali ko'rsatiladi.
    """
    queryset = MentorProfile.objects.select_related('user').order_by(
        '-is_featured', '-rating', '-students_helped'
    )
    serializer_class   = MentorSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends    = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields   = ['primary_track', 'offers_admission_support', 'is_featured']
    search_fields      = ['expertise', 'user__first_name', 'user__last_name',
                          'university_background', 'headline']
    ordering_fields    = ['rating', 'price_per_hour', 'students_helped', 'experience_years']

    def get_queryset(self):
        qs = super().get_queryset()
        price = self.request.query_params.get('max_price')
        if price:
            qs = qs.filter(price_per_hour__lte=price)
        return qs

    @action(detail=False, methods=['get'])
    def featured(self, request):
        """Top 6 featured mentor."""
        qs = self.get_queryset().filter(is_featured=True)[:6]
        return Response(self.get_serializer(qs, many=True).data)

    @action(detail=True, methods=['get'])
    def availability(self, request, pk=None):
        """Mentorning bo'sh vaqtlari."""
        mentor = self.get_object()
        slots  = MentorAvailability.objects.filter(mentor=mentor, is_available=True)
        return Response(MentorAvailabilitySerializer(slots, many=True).data)

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def favorite(self, request, pk=None):
        """Mentorni saqlash / saqlashdan olib tashlash."""
        mentor = self.get_object()
        obj, created = FavoriteMentor.objects.get_or_create(
            user=request.user, mentor=mentor
        )
        if not created:
            obj.delete()
            return Response({'status': 'removed'})
        return Response({'status': 'saved'})