from django.contrib import admin
from .models import HairStyleCategory, ClientImage, StyleRecommendation


@admin.register(HairStyleCategory)
class HairStyleCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'occasion', 'created_at')
    list_filter = ('occasion',)


@admin.register(ClientImage)
class ClientImageAdmin(admin.ModelAdmin):
    list_display = ('barber', 'client', 'hair_length', 'created_at')
    list_filter = ('hair_length',)
    raw_id_fields = ('barber', 'client')


@admin.register(StyleRecommendation)
class StyleRecommendationAdmin(admin.ModelAdmin):
    list_display = ('title', 'barber', 'client', 'category', 'created_at')
    search_fields = ('title', 'client__email', 'barber__business_name')
    raw_id_fields = ('barber', 'client', 'client_image')
