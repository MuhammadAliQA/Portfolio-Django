from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display  = ('username', 'email', 'first_name', 'last_name', 'role', 'is_staff', 'is_active', 'date_joined')
    list_filter   = ('role', 'is_staff', 'is_active')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    ordering      = ('-date_joined',)
    list_editable = ('role', 'is_active')

    fieldsets = UserAdmin.fieldsets + (
        ('EduBridge', {
            'fields': ('role', 'bio')
        }),
    )

    add_fieldsets = UserAdmin.add_fieldsets + (
        ('EduBridge', {
            'fields': ('role', 'bio')
        }),
    )