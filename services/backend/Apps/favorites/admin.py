from django.contrib import admin
from .models import Favorite


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('client', 'barber', 'created_at')
    search_fields = ('client__email', 'barber__business_name')
    raw_id_fields = ('client', 'barber')
