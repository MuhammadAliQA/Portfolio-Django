from django.contrib import admin
from .models import MentorProfile, MentorAvailability, FavoriteMentor


class AvailabilityInline(admin.TabularInline):
    model  = MentorAvailability
    extra  = 3
    fields = ('date', 'time', 'is_available')


@admin.register(MentorProfile)
class MentorProfileAdmin(admin.ModelAdmin):
    list_display   = ('user', 'primary_track', 'price_per_hour',
                      'rating', 'students_helped', 'is_featured', 'offers_admission_support')
    list_filter    = ('primary_track', 'is_featured', 'offers_admission_support')
    search_fields  = ('user__username', 'user__first_name', 'user__last_name', 'expertise')
    list_editable  = ('is_featured', 'offers_admission_support', 'price_per_hour')
    ordering       = ('-is_featured', '-rating')
    inlines        = [AvailabilityInline]
    fieldsets = (
        ('Asosiy ma\'lumot', {
            'fields': ('user', 'primary_track', 'expertise', 'headline',
                       'university_background', 'languages', 'about')
        }),
        ('Statistika', {
            'fields': ('experience_years', 'students_helped',
                       'success_story_count', 'rating')
        }),
        ('Sozlamalar', {
            'fields': ('price_per_hour', 'is_featured', 'offers_admission_support')
        }),
    )


@admin.register(MentorAvailability)
class MentorAvailabilityAdmin(admin.ModelAdmin):
    list_display  = ('mentor', 'date', 'time', 'is_available')
    list_filter   = ('is_available', 'date')
    ordering      = ('date', 'time')


@admin.register(FavoriteMentor)
class FavoriteMentorAdmin(admin.ModelAdmin):
    list_display = ('user', 'mentor', 'created_at')
    ordering     = ('-created_at',)