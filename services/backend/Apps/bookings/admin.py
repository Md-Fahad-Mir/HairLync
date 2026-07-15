from django.contrib import admin
from .models import Booking, TimeSlot


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'get_booking_type', 'client', 'barber', 'salon', 'employee',
        'service', 'date', 'start_time', 'status', 'created_at',
    )
    list_filter = ('status', 'date', 'salon')
    search_fields = ('client__email', 'barber__business_name', 'salon__business_name')
    raw_id_fields = ('client', 'barber', 'salon', 'employee', 'service')
    date_hierarchy = 'date'

    @admin.display(description='Type', ordering='salon')
    def get_booking_type(self, obj):
        return obj.booking_type


@admin.register(TimeSlot)
class TimeSlotAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'barber', 'salon', 'employee', 'date', 'start_time', 'end_time',
        'is_available', 'is_blocked',
    )
    list_filter = ('is_available', 'is_blocked', 'date', 'salon')
    raw_id_fields = ('barber', 'salon', 'employee')
