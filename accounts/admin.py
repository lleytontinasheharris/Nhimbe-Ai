"""Accounts admin configuration"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils import timezone
from django.utils.html import format_html
from .models import CustomUser


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = ['username', 'email', 'first_name', 'province', 'agritex_status_badge', 'date_joined']
    list_filter = ['is_agritex_officer', 'agritex_verification_status', 'province', 'preferred_language', 'is_staff']
    search_fields = ['username', 'email', 'first_name', 'last_name']
    ordering = ['-date_joined']

    fieldsets = UserAdmin.fieldsets + (
        ('Farmer Information', {
            'fields': ('bio', 'province', 'preferred_language', 'profile_picture', 'farming_experience', 'crops')
        }),
        ('AGRITEX Verification', {
            'fields': ('is_agritex_officer', 'agritex_verification_status', 'agritex_id_document', 
                      'agritex_verification_notes', 'agritex_applied_at', 'agritex_verified_at'),
            'classes': ('collapse',)
        }),
    )

    readonly_fields = ['agritex_applied_at', 'agritex_verified_at']

    actions = ['approve_agritex', 'reject_agritex']

    def agritex_status_badge(self, obj):
        if obj.agritex_verification_status == 'approved':
            return format_html('<span style="color: white; background: #2d5a3d; padding: 3px 8px; border-radius: 10px; font-size: 11px;">✓ AGRITEX</span>')
        elif obj.agritex_verification_status == 'pending':
            return format_html('<span style="color: #856404; background: #fff3cd; padding: 3px 8px; border-radius: 10px; font-size: 11px;">⏳ Pending</span>')
        elif obj.agritex_verification_status == 'rejected':
            return format_html('<span style="color: #721c24; background: #f8d7da; padding: 3px 8px; border-radius: 10px; font-size: 11px;">✗ Rejected</span>')
        return '-'
    agritex_status_badge.short_description = 'AGRITEX Status'

    @admin.action(description='Approve selected AGRITEX applications')
    def approve_agritex(self, request, queryset):
        count = 0
        for user in queryset.filter(agritex_verification_status='pending'):
            user.is_agritex_officer = True
            user.agritex_verification_status = 'approved'
            user.agritex_verified_at = timezone.now()
            user.save()
            count += 1
        self.message_user(request, f'{count} user(s) approved as AGRITEX officers.')

    @admin.action(description='Reject selected AGRITEX applications')
    def reject_agritex(self, request, queryset):
        count = queryset.filter(agritex_verification_status='pending').update(
            agritex_verification_status='rejected'
        )
        self.message_user(request, f'{count} AGRITEX application(s) rejected.')