from django.contrib import admin
from .models import ServiceCategory, Service


@admin.register(ServiceCategory)
class ServiceCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at')
    search_fields = ('name',)


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = (
        'name', 'get_owner_type', 'barber', 'salon', 'category', 'price',
        'duration_minutes', 'gender_target', 'is_active',
    )
    list_filter = ('category', 'gender_target', 'is_active', 'salon')
    search_fields = ('name', 'barber__business_name', 'salon__business_name')
    raw_id_fields = ('barber', 'salon')
    filter_horizontal = ('available_employees',)

    @admin.display(description='Owner', ordering='salon')
    def get_owner_type(self, obj):
        return obj.owner_type
