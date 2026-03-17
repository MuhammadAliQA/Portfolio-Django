from django.contrib import admin
from .models import Review


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display    = ('student', 'mentor', 'rating', 'created_at')
    list_filter     = ('rating',)
    search_fields   = ('student__username', 'mentor__user__username')
    ordering        = ('-created_at',)
    readonly_fields = ('created_at',)