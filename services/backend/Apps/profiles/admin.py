from django.contrib import admin
from .models import ClientProfile, BarberProfile, EmployeeProfile


@admin.register(ClientProfile)
class ClientProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'city', 'hair_type', 'created_at')
    list_filter = ('hair_type', 'gender')
    search_fields = ('user__email', 'user__full_name', 'city')
    raw_id_fields = ('user',)


@admin.register(BarberProfile)
class BarberProfileAdmin(admin.ModelAdmin):
    list_display = ('business_name', 'user', 'category', 'city', 'is_verified', 'average_rating', 'total_reviews', 'total_bookings')
    list_filter = ('category', 'is_verified', 'is_accepting_clients')
    search_fields = ('business_name', 'user__email', 'city')
    raw_id_fields = ('user',)
    list_editable = ('is_verified',)


@admin.register(EmployeeProfile)
class EmployeeProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'barber', 'position', 'is_active', 'can_manage_bookings', 'can_manage_schedule')
    list_filter = ('is_active', 'can_manage_bookings')
    search_fields = ('user__email', 'barber__business_name')
    raw_id_fields = ('user', 'barber')
