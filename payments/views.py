from django.utils import timezone
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Payment
from .serializers import PaymentSerializer


class PaymentViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class   = PaymentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Payment.objects.filter(
            user=self.request.user
        ).select_related('consultation', 'consultation__mentor', 'consultation__mentor__user').order_by('-created_at')

    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        payment = self.get_object()
        if payment.status == "paid":
            return Response({"detail": "Payment is already completed."}, status=status.HTTP_400_BAD_REQUEST)
        payment.status = "paid"
        payment.paid_at = timezone.now()
        payment.save(update_fields=["status", "paid_at"])
        return Response({"status": payment.status, "paid_at": payment.paid_at})
