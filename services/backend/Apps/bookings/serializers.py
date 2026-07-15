from datetime import datetime

from django.conf import settings
from django.db import connection, transaction
from django.utils import timezone
from rest_framework import serializers

from Apps.profiles.models import SalonProfile, SalonEmployee
from Apps.services.models import Service
from .models import Booking, TimeSlot, ACTIVE_BOOKING_STATUSES


# ------------------------------------------------------------------------------
# Shared helpers
# ------------------------------------------------------------------------------
def _minutes_between(start_time, end_time):
    """Duration in whole minutes between two naive times on the same day."""
    today = timezone.now().date()
    delta = datetime.combine(today, end_time) - datetime.combine(today, start_time)
    return int(delta.total_seconds() // 60)


def _is_in_past(date, start_time):
    """True if the given date/time is already in the past."""
    booking_dt = datetime.combine(date, start_time)
    if settings.USE_TZ:
        return timezone.make_aware(booking_dt) < timezone.now()
    return booking_dt < datetime.now()


def employee_can_provide(service, employee):
    """
    Employee eligibility rule for a salon service:
      - no `available_employees` configured -> every active salon employee may provide it
      - otherwise -> only the listed employees may
    """
    if not service.available_employees.exists():
        return True
    return service.available_employees.filter(pk=employee.pk).exists()


def employee_has_availability(employee, date, start_time, end_time):
    """True if a salon availability slot fully covers the requested window."""
    return TimeSlot.objects.filter(
        salon_id=employee.salon_id,
        employee=employee,
        date=date,
        is_available=True,
        is_blocked=False,
        start_time__lte=start_time,
        end_time__gte=end_time,
    ).exists()


def employee_conflicting_bookings(employee, date, start_time, end_time, exclude_pk=None):
    """
    Employee-level overlap query. Deliberately independent of `Booking.barber`.
    Overlap := existing.start < requested_end AND existing.end > requested_start
    """
    qs = Booking.objects.filter(
        employee=employee,
        date=date,
        status__in=ACTIVE_BOOKING_STATUSES,
        start_time__lt=end_time,
        end_time__gt=start_time,
    )
    if exclude_pk is not None:
        qs = qs.exclude(pk=exclude_pk)
    return qs


# ------------------------------------------------------------------------------
# BOOKING SERIALIZERS (shared - must stay backward compatible for barbers)
# ------------------------------------------------------------------------------
class BookingSerializer(serializers.ModelSerializer):
    """
    Shared read serializer for both booking shapes.

    Barber bookings keep every field/value they had before. Salon bookings reuse
    the same envelope with `barber`/`barber_name` null and the salon fields set.
    All name fields are method fields so a null FK yields null instead of
    raising AttributeError or being silently dropped from the payload.
    """
    client_name = serializers.CharField(source='client.full_name', read_only=True)
    client_email = serializers.CharField(source='client.email', read_only=True)
    barber_name = serializers.SerializerMethodField()
    salon_name = serializers.SerializerMethodField()
    employee_name = serializers.SerializerMethodField()
    service_name = serializers.SerializerMethodField()
    booking_type = serializers.SerializerMethodField()
    can_cancel = serializers.SerializerMethodField()

    class Meta:
        model = Booking
        fields = '__all__'
        read_only_fields = [
            'client', 'status', 'barber_notes', 'cancellation_reason',
            'rejection_reason', 'rescheduled_from', 'created_at', 'updated_at',
        ]

    def get_barber_name(self, obj):
        return obj.barber.business_name if obj.barber_id else None

    def get_salon_name(self, obj):
        return obj.salon.business_name if obj.salon_id else None

    def get_employee_name(self, obj):
        return obj.employee.user.full_name if obj.employee_id else None

    def get_service_name(self, obj):
        return obj.service.name if obj.service_id else None

    def get_booking_type(self, obj):
        return obj.booking_type

    def get_can_cancel(self, obj):
        return obj.can_cancel()


class BookingCreateSerializer(serializers.ModelSerializer):
    """
    Barber booking creation (existing, frontend-integrated endpoint).

    Behaviour for barber payloads is unchanged. `salon` is deliberately absent
    so this endpoint can never create a salon booking.
    """
    class Meta:
        model = Booking
        fields = ['barber', 'employee', 'service', 'date', 'start_time', 'end_time', 'notes']

    def validate_barber(self, value):
        if value is None:
            raise serializers.ValidationError("This field is required.")
        return value

    def validate(self, attrs):
        if attrs['start_time'] >= attrs['end_time']:
            raise serializers.ValidationError({"end_time": "End time must be after start time."})

        # Check for conflicts
        barber = attrs['barber']
        date = attrs['date']
        start = attrs['start_time']
        end = attrs['end_time']

        # A barber booking must not carry a salon employee: the two business
        # shapes are mutually exclusive (see Booking model docstring).
        if attrs.get('employee'):
            raise serializers.ValidationError({
                "employee": (
                    "A barber booking cannot reference a salon employee. "
                    "Use the salon booking endpoint instead."
                )
            })

        if attrs.get('service') and attrs['service'].barber_id != barber.id:
            raise serializers.ValidationError({
                "service": "The selected service does not belong to this barber."
            })

        conflicts = Booking.objects.filter(
            barber=barber,
            date=date,
            status__in=ACTIVE_BOOKING_STATUSES,
            start_time__lt=end,
            end_time__gt=start,
        )

        if conflicts.exists():
            raise serializers.ValidationError("This time slot conflicts with an existing booking.")

        return attrs


class BookingStatusUpdateSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=['approved', 'rejected', 'completed', 'cancelled'])
    reason = serializers.CharField(required=False, default='')


class BookingRescheduleSerializer(serializers.Serializer):
    new_date = serializers.DateField()
    new_start_time = serializers.TimeField()
    new_end_time = serializers.TimeField()

    def validate(self, attrs):
        if attrs['new_start_time'] >= attrs['new_end_time']:
            raise serializers.ValidationError({"new_end_time": "End time must be after start time."})
        return attrs


class TimeSlotSerializer(serializers.ModelSerializer):
    class Meta:
        model = TimeSlot
        fields = '__all__'
        # `salon` is read-only so the barber slot endpoint cannot set it.
        read_only_fields = ['barber', 'salon', 'created_at']


class TimeSlotCreateSerializer(serializers.ModelSerializer):
    """Barber availability creation. Field list intentionally unchanged."""
    class Meta:
        model = TimeSlot
        fields = ['employee', 'date', 'start_time', 'end_time', 'is_available', 'is_blocked']


# ==============================================================================
# SALON BOOKING SERIALIZERS
# ==============================================================================
class SalonBookingCreateSerializer(serializers.ModelSerializer):
    """
    Salon booking creation.

    Every relationship supplied by the client is re-verified against the
    database: the salon must be bookable, the employee must belong to that
    salon and be active, and the service must belong to that salon and be
    providable by that employee. The client is assigned from the request and is
    never accepted from the payload.
    """
    salon = serializers.PrimaryKeyRelatedField(queryset=SalonProfile.objects.all())
    employee = serializers.PrimaryKeyRelatedField(queryset=SalonEmployee.objects.all())
    service = serializers.PrimaryKeyRelatedField(queryset=Service.objects.all())

    class Meta:
        model = Booking
        fields = ['salon', 'employee', 'service', 'date', 'start_time', 'end_time', 'notes']

    def validate(self, attrs):
        salon = attrs['salon']
        employee = attrs['employee']
        service = attrs['service']
        date = attrs['date']
        start = attrs['start_time']
        end = attrs['end_time']

        # --- salon ---------------------------------------------------------
        if not salon.user.is_active:
            raise serializers.ValidationError({"salon": "This salon is not available for booking."})
        if not salon.is_accepting_clients:
            raise serializers.ValidationError({"salon": "This salon is not currently accepting clients."})

        # --- employee ------------------------------------------------------
        if employee.salon_id != salon.id:
            raise serializers.ValidationError({"employee": "This employee does not belong to the selected salon."})
        if not employee.is_active:
            raise serializers.ValidationError({"employee": "This employee is not currently available."})
        if not employee.user.is_active:
            raise serializers.ValidationError({"employee": "This employee is not currently available."})

        # --- service -------------------------------------------------------
        if service.salon_id != salon.id:
            raise serializers.ValidationError({"service": "This service does not belong to the selected salon."})
        if not service.is_active:
            raise serializers.ValidationError({"service": "This service is not currently available."})
        if not employee_can_provide(service, employee):
            raise serializers.ValidationError({"service": "The selected employee does not provide this service."})

        # --- date / time ---------------------------------------------------
        if start >= end:
            raise serializers.ValidationError({"end_time": "End time must be after start time."})
        if _is_in_past(date, start):
            raise serializers.ValidationError({"date": "Cannot create a booking in the past."})
        if service.duration_minutes:
            requested = _minutes_between(start, end)
            if requested != service.duration_minutes:
                raise serializers.ValidationError({
                    "end_time": (
                        f"This service takes {service.duration_minutes} minutes; "
                        f"the requested window is {requested} minutes."
                    )
                })

        # --- availability ---------------------------------------------------
        if not employee_has_availability(employee, date, start, end):
            raise serializers.ValidationError({
                "start_time": "The selected employee is not available at this time."
            })

        # --- conflicts (employee-level; independent of Booking.barber) -------
        if employee_conflicting_bookings(employee, date, start, end).exists():
            raise serializers.ValidationError(
                "This time slot conflicts with an existing booking for this employee."
            )

        return attrs

    def create(self, validated_data):
        employee = validated_data['employee']
        date = validated_data['date']
        start = validated_data['start_time']
        end = validated_data['end_time']

        with transaction.atomic():
            # Re-check under a transaction to narrow the check-then-act window
            # between validate() and the INSERT.
            conflicts = employee_conflicting_bookings(employee, date, start, end)
            if connection.features.has_select_for_update:
                conflicts = conflicts.select_for_update()
            if conflicts.exists():
                raise serializers.ValidationError(
                    "This time slot conflicts with an existing booking for this employee."
                )
            validated_data['barber'] = None
            return super().create(validated_data)


class SalonTimeSlotSerializer(serializers.ModelSerializer):
    """Read serializer for salon employee availability."""
    employee_name = serializers.SerializerMethodField()

    class Meta:
        model = TimeSlot
        fields = [
            'id', 'salon', 'employee', 'employee_name', 'date', 'start_time',
            'end_time', 'is_available', 'is_blocked', 'created_at',
        ]
        read_only_fields = ['id', 'salon', 'employee', 'created_at']

    def get_employee_name(self, obj):
        return obj.employee.user.full_name if obj.employee_id else None


class SalonPublicTimeSlotSerializer(serializers.ModelSerializer):
    """Public availability payload. Exposes no employee credentials or PII."""
    class Meta:
        model = TimeSlot
        fields = ['id', 'employee', 'date', 'start_time', 'end_time']


class SalonTimeSlotCreateUpdateSerializer(serializers.ModelSerializer):
    """
    Create/update salon employee availability.

    `salon`/`employee` are resolved by the view from the authenticated user (or
    validated against the owner's salon) and are never taken from the payload.
    """
    class Meta:
        model = TimeSlot
        fields = ['date', 'start_time', 'end_time', 'is_available', 'is_blocked']

    def validate(self, attrs):
        start = attrs.get('start_time', getattr(self.instance, 'start_time', None))
        end = attrs.get('end_time', getattr(self.instance, 'end_time', None))
        if start and end and start >= end:
            raise serializers.ValidationError({"end_time": "End time must be after start time."})
        return attrs
