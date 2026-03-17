from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Consultation
from .serializers import ConsultationSerializer
from payments.models import Payment


class ConsultationViewSet(viewsets.ModelViewSet):
    serializer_class   = ConsultationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user

        if user.role == 'mentor':
            return Consultation.objects.select_related(
                'student', 'mentor', 'mentor__user'
            ).filter(mentor__user=user).order_by('-date', '-time')
        return Consultation.objects.select_related(
            'student', 'mentor', 'mentor__user'
        ).filter(student=user).order_by('-date', '-time')

    def perform_create(self, serializer):
        consultation = serializer.save(student=self.request.user)
        if not consultation.is_free_intro_call:
            amount = (consultation.mentor.price_per_hour * consultation.duration_minutes) / 60
            Payment.objects.get_or_create(
                consultation=consultation,
                defaults={
                    "user": self.request.user,
                    "amount": amount,
                    "status": "pending",
                },
            )

    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """Sessiyani bekor qilish."""
        consultation = self.get_object()
        if consultation.student != request.user:
            return Response({'error': 'Ruxsat yo\'q'}, status=status.HTTP_403_FORBIDDEN)
        if consultation.status == 'completed':
            return Response({'error': 'Yakunlangan sessiya bekor qilinmaydi'},
                            status=status.HTTP_400_BAD_REQUEST)
        consultation.status = 'cancelled'
        consultation.save()
        return Response({'status': 'cancelled'})

    @action(detail=True, methods=['post'])
    def confirm(self, request, pk=None):
        """Mentor sessiyani tasdiqlaydi."""
        consultation = self.get_object()
        if consultation.mentor.user != request.user:
            return Response({'error': 'Faqat mentor tasdiqlaydi'},
                            status=status.HTTP_403_FORBIDDEN)
        if consultation.status == 'cancelled':
            return Response({'error': 'Bekor qilingan sessiya tasdiqlanmaydi'},
                            status=status.HTTP_400_BAD_REQUEST)
        if not consultation.is_free_intro_call:
            payment = Payment.objects.filter(consultation=consultation).first()
            if not payment or payment.status != "paid":
                return Response(
                    {'error': 'To\'lov yakunlanmaguncha sessiya tasdiqlanmaydi'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        consultation.status = 'confirmed'
        consultation.save()
        return Response({'status': 'confirmed'})
