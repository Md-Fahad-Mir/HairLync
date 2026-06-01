from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import CustomUserModel, PendingUser, ForgotPasswordRequest


@admin.register(CustomUserModel)
class CustomUserAdmin(BaseUserAdmin):
    list_display = ('email', 'full_name', 'role', 'is_active', 'is_verified', 'paid_user', 'current_plan', 'date_joined')
    list_filter = ('role', 'is_active', 'is_verified', 'is_staff', 'paid_user', 'current_plan')
    search_fields = ('email', 'full_name', 'phone_number')
    ordering = ('-date_joined',)

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal Info', {'fields': ('full_name', 'phone_number', 'country')}),
        ('Role & Status', {'fields': ('role', 'is_active', 'is_verified')}),
        ('Subscription', {'fields': ('paid_user', 'current_plan', 'current_period_start', 'current_period_end')}),
        ('Permissions', {'fields': ('is_staff', 'is_superuser', 'groups', 'user_permissions')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'full_name', 'role', 'password1', 'password2', 'is_active', 'is_verified'),
        }),
    )


@admin.register(PendingUser)
class PendingUserAdmin(admin.ModelAdmin):
    list_display = ('email', 'full_name', 'role', 'otp', 'created_at', 'otp_created_at')
    list_filter = ('role',)
    search_fields = ('email', 'full_name')
    readonly_fields = ('created_at', 'otp_created_at')


@admin.register(ForgotPasswordRequest)
class ForgotPasswordRequestAdmin(admin.ModelAdmin):
    list_display = ('email', 'otp', 'created_at', 'otp_created_at')
    search_fields = ('email',)
    readonly_fields = ('created_at', 'otp_created_at')
