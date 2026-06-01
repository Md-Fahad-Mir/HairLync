from django.contrib import admin
from .models import Booking, TimeSlot


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('id', 'client', 'barber', 'service', 'date', 'start_time', 'status', 'created_at')
    list_filter = ('status', 'date')
    search_fields = ('client__email', 'barber__business_name')
    raw_id_fields = ('client', 'barber', 'employee', 'service')
    date_hierarchy = 'date'


@admin.register(TimeSlot)
class TimeSlotAdmin(admin.ModelAdmin):
    list_display = ('barber', 'date', 'start_time', 'end_time', 'is_available', 'is_blocked')
    list_filter = ('is_available', 'is_blocked', 'date')
    raw_id_fields = ('barber', 'employee')
