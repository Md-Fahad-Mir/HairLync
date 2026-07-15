from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.core.validators import MinValueValidator


# Statuses that occupy a slot and therefore participate in conflict detection.
ACTIVE_BOOKING_STATUSES = ('pending', 'approved')


# ------------------------------------------------------------------------------
# BOOKING / APPOINTMENT
# ------------------------------------------------------------------------------
class Booking(models.Model):
    """
    Appointment booking.

    A booking is owned by exactly ONE business, expressed as one of two shapes:

    Barber booking (legacy, frontend-integrated):
        barber = BarberProfile, salon = None, employee = None

    Salon booking:
        barber = None, salon = SalonProfile, employee = SalonEmployee (required)

    The `salon` FK is stored directly on the booking (rather than being derived
    from `employee.salon`) so ownership, filtering and permissions stay correct
    even if an employee is later moved or removed.
    """

    class Meta:
        verbose_name = 'Booking'
        verbose_name_plural = 'Bookings'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', 'date']),
            models.Index(fields=['barber', 'date']),
            models.Index(fields=['client', 'status']),
            models.Index(fields=['salon', 'date']),
            models.Index(fields=['salon', 'status']),
            models.Index(fields=['employee', 'date']),
        ]
        constraints = [
            # Exactly one business owner. Existing barber rows satisfy this
            # (barber set, salon NULL), so the constraint is safe to add.
            models.CheckConstraint(
                condition=(
                    models.Q(barber__isnull=False, salon__isnull=True)
                    | models.Q(barber__isnull=True, salon__isnull=False)
                ),
                name='booking_exactly_one_business',
            ),
            # A salon booking must name the employee being booked. Existing
            # barber rows have salon NULL, so they are unaffected.
            models.CheckConstraint(
                condition=(
                    models.Q(salon__isnull=True) | models.Q(employee__isnull=False)
                ),
                name='booking_salon_requires_employee',
            ),
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
        null=True,
        blank=True,
        related_name='bookings',
        help_text='Set for barber bookings. Null for salon bookings.',
    )
    salon = models.ForeignKey(
        'profiles.SalonProfile',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='bookings',
        help_text='Set for salon bookings. Null for barber bookings.',
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
        business = self.business_name or 'Unknown'
        return f"Booking #{self.id}: {self.client.email} -> {business} on {self.date}"

    @property
    def is_salon_booking(self):
        return self.salon_id is not None

    @property
    def booking_type(self):
        return 'salon' if self.salon_id else 'barber'

    @property
    def business_name(self):
        """Display name of the owning business, whichever shape this booking is."""
        if self.salon_id:
            return self.salon.business_name
        if self.barber_id:
            return self.barber.business_name
        return None

    def clean(self):
        """Model-level guard against invalid barber/salon/employee combinations."""
        errors = {}

        if not self.barber_id and not self.salon_id:
            errors['barber'] = 'A booking must belong to either a barber or a salon.'
        elif self.barber_id and self.salon_id:
            errors['salon'] = 'A booking cannot belong to both a barber and a salon.'

        if self.salon_id:
            if not self.employee_id:
                errors['employee'] = 'A salon booking must specify an employee.'
            elif self.employee.salon_id != self.salon_id:
                errors['employee'] = 'The employee does not belong to the selected salon.'
        elif self.barber_id and self.employee_id:
            errors['employee'] = 'A barber booking cannot reference a salon employee.'

        if self.start_time and self.end_time and self.start_time >= self.end_time:
            errors['end_time'] = 'End time must be after start time.'

        if self.service_id:
            if self.salon_id and self.service.salon_id != self.salon_id:
                errors['service'] = 'The service does not belong to the selected salon.'
            if self.barber_id and self.service.barber_id != self.barber_id:
                errors['service'] = 'The service does not belong to the selected barber.'

        if errors:
            raise ValidationError(errors)

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
    """
    Availability slot, owned by exactly ONE business:

    Barber availability (legacy):
        barber = BarberProfile, salon = None, employee = None

    Salon employee availability:
        barber = None, salon = SalonProfile, employee = SalonEmployee (required)
    """

    class Meta:
        verbose_name = 'Time Slot'
        verbose_name_plural = 'Time Slots'
        ordering = ['date', 'start_time']
        # Retained for barber slots. Salon slots have barber=NULL and SQL treats
        # NULLs as distinct, so they never collide here; they are covered by the
        # salon-scoped unique constraint below instead.
        unique_together = ('barber', 'date', 'start_time')
        indexes = [
            models.Index(fields=['employee', 'date']),
            models.Index(fields=['salon', 'date']),
        ]
        constraints = [
            models.CheckConstraint(
                condition=(
                    models.Q(barber__isnull=False, salon__isnull=True)
                    | models.Q(barber__isnull=True, salon__isnull=False)
                ),
                name='timeslot_exactly_one_business',
            ),
            models.CheckConstraint(
                condition=(
                    models.Q(salon__isnull=True) | models.Q(employee__isnull=False)
                ),
                name='timeslot_salon_requires_employee',
            ),
            # Scoped to salon slots only, so pre-existing barber rows can never
            # violate it when the migration is applied.
            models.UniqueConstraint(
                fields=['employee', 'date', 'start_time'],
                condition=models.Q(salon__isnull=False),
                name='uniq_salon_employee_slot',
            ),
        ]

    barber = models.ForeignKey(
        'profiles.BarberProfile',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='time_slots',
        help_text='Set for barber availability. Null for salon availability.',
    )
    salon = models.ForeignKey(
        'profiles.SalonProfile',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='time_slots',
        help_text='Set for salon availability. Null for barber availability.',
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
        if self.salon_id:
            owner = f"{self.salon.business_name} / {self.employee.user.full_name}" if self.employee_id \
                else self.salon.business_name
        elif self.barber_id:
            owner = self.barber.business_name
        else:
            owner = 'Unknown'
        return f"{owner} - {self.date} {self.start_time}-{self.end_time} ({status})"

    def clean(self):
        errors = {}

        if not self.barber_id and not self.salon_id:
            errors['barber'] = 'A time slot must belong to either a barber or a salon.'
        elif self.barber_id and self.salon_id:
            errors['salon'] = 'A time slot cannot belong to both a barber and a salon.'

        if self.salon_id:
            if not self.employee_id:
                errors['employee'] = 'A salon time slot must specify an employee.'
            elif self.employee.salon_id != self.salon_id:
                errors['employee'] = 'The employee does not belong to the selected salon.'

        if self.start_time and self.end_time and self.start_time >= self.end_time:
            errors['end_time'] = 'End time must be after start time.'

        if errors:
            raise ValidationError(errors)
