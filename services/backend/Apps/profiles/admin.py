from django.contrib import admin
from .models import ClientProfile, BarberProfile, SalonProfile, SalonEmployee, ProfileService



class BarberServiceManagementInline(admin.TabularInline):
    model = ProfileService
    fk_name = 'barber'
    extra = 1
    fields = ('service_name', 'price', 'duration_minutes', 'image', 'is_active')


class SalonServiceManagementInline(admin.TabularInline):
    model = ProfileService
    fk_name = 'salon'
    extra = 1
    fields = ('service_name', 'price', 'duration_minutes', 'image', 'is_active')


class EmployeeServiceManagementInline(admin.TabularInline):
    model = ProfileService
    fk_name = 'employee'
    extra = 1
    fields = ('service_name', 'price', 'duration_minutes', 'image', 'is_active')


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
    inlines = (BarberServiceManagementInline,)


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
    inlines = (SalonServiceManagementInline,)

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
    inlines = (EmployeeServiceManagementInline,)

@admin.register(ProfileService)
class ProfileServiceAdmin(admin.ModelAdmin):
    list_display = (
        'service_name', 'barber', 'salon', 'employee',
        'price', 'duration_minutes', 'is_active',
    )
    list_filter = ('is_active',)
    search_fields = (
        'service_name', 'barber__business_name', 'salon__business_name',
        'employee__user__full_name',
    )
    raw_id_fields = ('barber', 'salon', 'employee')

