"""Accounts admin configuration"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = ['username', 'email', 'province', 'farming_experience', 'is_active']
    list_filter = ['province', 'preferred_language', 'is_active']

    fieldsets = UserAdmin.fieldsets + (
        ('Farmer Info', {
            'fields': ('bio', 'province', 'preferred_language',
                       'profile_picture', 'farming_experience', 'crops')
        }),
    )