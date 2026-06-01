from django.contrib import admin
from .models import Review


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('client', 'barber', 'rating', 'is_approved', 'is_flagged', 'created_at')
    list_filter = ('rating', 'is_approved', 'is_flagged')
    search_fields = ('client__email', 'barber__business_name', 'comment')
    raw_id_fields = ('client', 'barber', 'booking')
    list_editable = ('is_approved', 'is_flagged')
