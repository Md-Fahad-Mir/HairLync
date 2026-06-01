from django.contrib import admin
from .models import ServiceCategory, Service


@admin.register(ServiceCategory)
class ServiceCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at')
    search_fields = ('name',)


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ('name', 'barber', 'category', 'price', 'duration_minutes', 'gender_target', 'is_active')
    list_filter = ('category', 'gender_target', 'is_active')
    search_fields = ('name', 'barber__business_name')
    raw_id_fields = ('barber',)
