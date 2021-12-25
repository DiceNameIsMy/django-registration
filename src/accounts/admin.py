from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from django.utils.translation import gettext_lazy as _


from .models import CustomUser, VerificationCode


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'phone', 'first_name', 'last_name', 'is_verified',  'is_staff')
    list_filter = ('is_verified', 'is_staff', 'is_superuser', 'is_active', 'is_verified', 'groups')
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'email', 'phone')}),
        (_('2FA'), {'fields': ('two_fa_enabled', 'two_fa_type')}),
        (_('Permissions'), {
            'fields': ('is_verified', 'is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )


@admin.register(VerificationCode)
class VerificationCodeAdmin(admin.ModelAdmin):
    list_display = ('user', 'type', 'code', 'created_at', 'is_used')
    list_filter = ('type', 'is_used')
