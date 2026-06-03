from django.db import models
from django.conf import settings
from django.utils import timezone
from django.core.validators import MinValueValidator


# ------------------------------------------------------------------------------
# BOOKING / APPOINTMENT
# ------------------------------------------------------------------------------
class Booking(models.Model):
    """Appointment booking between client and barber/employee."""

    class Meta:
        verbose_name = 'Booking'
        verbose_name_plural = 'Bookings'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', 'date']),
            models.Index(fields=['barber', 'date']),
            models.Index(fields=['client', 'status']),
        ]

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
        ('rescheduled', 'Rescheduled'),
    ]

    client = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='client_bookings',
        limit_choices_to={'role': 'client'},
    )
    barber = models.ForeignKey(
        'profiles.BarberProfile',
        on_delete=models.CASCADE,
        related_name='bookings',
    )
    employee = models.ForeignKey(
        'profiles.SalonEmployee',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='bookings',
    )
    service = models.ForeignKey(
        'services.Service',
        on_delete=models.SET_NULL,
        null=True,
        related_name='bookings',
    )

    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', db_index=True)

    notes = models.TextField(blank=True, default='', help_text='Client notes for the appointment')
    barber_notes = models.TextField(blank=True, default='', help_text='Barber internal notes')
    cancellation_reason = models.TextField(blank=True, default='')
    rejection_reason = models.TextField(blank=True, default='')

    # Rescheduling
    rescheduled_from = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='rescheduled_to',
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Booking #{self.id}: {self.client.email} -> {self.barber.business_name} on {self.date}"

    @property
    def is_upcoming(self):
        now = timezone.now()
        booking_datetime = timezone.make_aware(
            timezone.datetime.combine(self.date, self.start_time)
        )
        return booking_datetime > now and self.status in ('pending', 'approved')

    def can_cancel(self):
        """Check if the booking can still be cancelled (at least 2 hours before)."""
        if self.status not in ('pending', 'approved'):
            return False
        now = timezone.now()
        booking_datetime = timezone.make_aware(
            timezone.datetime.combine(self.date, self.start_time)
        )
        return (booking_datetime - now).total_seconds() > 7200  # 2 hours


# ------------------------------------------------------------------------------
# TIME SLOT / AVAILABILITY
# ------------------------------------------------------------------------------
class TimeSlot(models.Model):
    """Available time slots for a barber."""

    class Meta:
        verbose_name = 'Time Slot'
        verbose_name_plural = 'Time Slots'
        ordering = ['date', 'start_time']
        unique_together = ('barber', 'date', 'start_time')

    barber = models.ForeignKey(
        'profiles.BarberProfile',
        on_delete=models.CASCADE,
        related_name='time_slots',
    )
    employee = models.ForeignKey(
        'profiles.SalonEmployee',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='time_slots',
    )
    date = models.DateField(db_index=True)
    start_time = models.TimeField()
    end_time = models.TimeField()
    is_available = models.BooleanField(default=True)
    is_blocked = models.BooleanField(default=False, help_text='Manually blocked by barber')

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        status = "Available" if self.is_available and not self.is_blocked else "Unavailable"
        return f"{self.barber.business_name} - {self.date} {self.start_time}-{self.end_time} ({status})"
