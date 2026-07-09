from django.contrib import admin
from .models import ClientProfile, BarberProfile, SalonProfile, SalonEmployee


@admin.register(ClientProfile)
class ClientProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'city', 'hair_type', 'created_at')
    list_filter = ('hair_type', 'gender')
    search_fields = ('user__email', 'user__full_name', 'city')
    raw_id_fields = ('user',)


@admin.register(BarberProfile)
class BarberProfileAdmin(admin.ModelAdmin):
    list_display = (
        'business_name', 'user', 'category', 'city', 'is_verified',
        'average_rating', 'total_reviews', 'total_bookings',
    )
    list_filter = ('category', 'is_verified', 'is_accepting_clients', 'experience_range')
    search_fields = ('business_name', 'user__email', 'city')
    raw_id_fields = ('user',)
    list_editable = ('is_verified',)


@admin.register(SalonProfile)
class SalonProfileAdmin(admin.ModelAdmin):
    list_display = (
        'business_name', 'user', 'city', 'is_verified',
        'average_rating', 'total_reviews', 'total_bookings',
        'get_employees_count',
    )
    list_filter = ('is_verified', 'is_accepting_clients', 'experience_range')
    search_fields = ('business_name', 'user__email', 'city')
    raw_id_fields = ('user',)
    list_editable = ('is_verified',)

    @admin.display(description='Employees')
    def get_employees_count(self, obj):
        return obj.employees.filter(is_active=True).count()


@admin.register(SalonEmployee)
class SalonEmployeeAdmin(admin.ModelAdmin):
    list_display = (
        'user', 'salon', 'position', 'generated_email',
        'is_active', 'average_rating', 'total_bookings',
    )
    list_filter = ('is_active', 'position')
    search_fields = ('user__email', 'user__full_name', 'salon__business_name', 'generated_email')
    raw_id_fields = ('user', 'salon')
    readonly_fields = ('generated_email', 'generated_password')
