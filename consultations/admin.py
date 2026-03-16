from django.contrib import admin
from .models import Consultation


@admin.register(Consultation)
class ConsultationAdmin(admin.ModelAdmin):
    list_display   = ('student', 'mentor', 'date', 'time',
                      'service_type', 'status', 'is_free_intro_call', 'created_at')
    list_filter    = ('status', 'service_type', 'is_free_intro_call', 'date')
    search_fields  = ('student__username', 'mentor__user__username')
    list_editable  = ('status',)
    ordering       = ('-date', '-time')
    date_hierarchy = 'date'
    readonly_fields = ('created_at',)