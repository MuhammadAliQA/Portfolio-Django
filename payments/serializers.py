from rest_framework import serializers
from .models import Payment


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Payment
        fields = ['id', 'user', 'consultation', 'amount', 'status', 'created_at', 'paid_at']
        read_only_fields = ['id', 'created_at', 'paid_at', 'user', 'amount', 'status']
