from django.contrib import admin
from .models import Payment


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display  = ('user', 'consultation', 'amount', 'status', 'created_at')
    list_filter   = ('status',)
    search_fields = ('user__username', 'user__email')
    ordering      = ('-created_at',)