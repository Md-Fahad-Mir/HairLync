from django.contrib import admin
from .models import EducationCategory, EducationalContent


@admin.register(EducationCategory)
class EducationCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at')
    search_fields = ('name',)


@admin.register(EducationalContent)
class EducationalContentAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'content_type', 'difficulty', 'is_premium', 'is_published', 'view_count')
    list_filter = ('content_type', 'difficulty', 'is_premium', 'is_published')
    search_fields = ('title', 'description')
    prepopulated_fields = {'slug': ('title',)}
    list_editable = ('is_published',)
