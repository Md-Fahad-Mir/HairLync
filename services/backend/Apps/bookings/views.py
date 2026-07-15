from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.db import IntegrityError, transaction
from django.db.models import Exists, F, OuterRef
from django.utils import timezone
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from .models import Booking, TimeSlot, ACTIVE_BOOKING_STATUSES
from .serializers import (
    BookingSerializer, BookingCreateSerializer,
    BookingStatusUpdateSerializer, BookingRescheduleSerializer,
    TimeSlotSerializer, TimeSlotCreateSerializer,
    SalonBookingCreateSerializer, SalonTimeSlotSerializer,
    SalonPublicTimeSlotSerializer, SalonTimeSlotCreateUpdateSerializer,
    employee_can_provide, employee_has_availability, employee_conflicting_bookings,
)
from Apps.users.permissions import (
    IsClient, IsBarber, IsBarberOrSubBarber,
    IsSalonOwner, IsSalonEmployee, IsSalonOrEmployee,
)
from Apps.users.utils import success_response, error_response
from Apps.profiles.models import BarberProfile, SalonProfile, SalonEmployee


# ==============================================================================
# SHARED HELPERS
# ==============================================================================
# Status transitions, shared by the barber and salon status endpoints.
VALID_STATUS_TRANSITIONS = {
    'pending': ['approved', 'rejected'],
    'approved': ['completed', 'cancelled'],
}


def _get_salon_profile(request):
    """The authenticated salon owner's profile, or None."""
    try:
        return request.user.salon_profile
    except SalonProfile.DoesNotExist:
        return None


def _apply_date_filters(qs, request):
    """Shared `date_from` / `date_to` range filtering."""
    date_from = request.query_params.get('date_from')
    date_to = request.query_params.get('date_to')
    if date_from:
        qs = qs.filter(date__gte=date_from)
    if date_to:
        qs = qs.filter(date__lte=date_to)
    return qs


def _create_salon_slot(serializer, employee):
    """
    Persist a salon availability slot for `employee`, deriving salon/employee
    from the server side. Returns None if it collides with an existing slot.
    """
    try:
        with transaction.atomic():
            return serializer.save(
                barber=None, salon=employee.salon, employee=employee
            )
    except IntegrityError:
        # uniq_salon_employee_slot
        return None


def _get_employee_booking(request, pk):
    """
    Tenant-scoped single-booking lookup for a salon employee.

    Scoped in the query on employee AND salon, so another employee's booking is
    never fetched in the first place (no post-hoc Python check).
    """
    employee = SalonEmployee.objects.filter(user=request.user).first()
    if not employee:
        return None
    return Booking.objects.filter(
        pk=pk, employee=employee, salon_id=employee.salon_id
    ).first()


def _get_salon_manageable_booking(request, pk):
    """
    Fetch a salon booking the requesting user is allowed to manage.

    Owner  -> any booking of their own salon.
    Employee -> only bookings assigned to them, within their salon.
    Both paths scope in the database, never globally.
    """
    user = request.user
    if user.is_salon_owner:
        salon = _get_salon_profile(request)
        if not salon:
            return None
        return Booking.objects.filter(pk=pk, salon=salon).first()
    if user.is_salon_employee:
        return _get_employee_booking(request, pk)
    return None


def _increment_completed_counter(booking):
    """
    Bump the completed-booking counter for whichever business owns the booking.

    Uses F() so concurrent completions cannot lose an increment. Barber bookings
    keep their existing behaviour (BarberProfile.total_bookings); salon bookings
    credit the employee who performed the service. No new denormalised salon
    counter is introduced - SalonProfile.total_bookings already exists but is
    not currently maintained anywhere, so it is left untouched.
    """
    if booking.barber_id:
        BarberProfile.objects.filter(pk=booking.barber_id).update(
            total_bookings=F('total_bookings') + 1
        )
    elif booking.employee_id:
        SalonEmployee.objects.filter(pk=booking.employee_id).update(
            total_bookings=F('total_bookings') + 1
        )


# ==============================================================================
# BOOKING VIEWS (CLIENT)
# ==============================================================================
class ClientBookingCreateView(APIView):
    """Create a new booking (client only)."""
    permission_classes = [IsAuthenticated, IsClient]

    @swagger_auto_schema(
        operation_description="Create a new appointment booking.",
        request_body=BookingCreateSerializer,
        responses={201: BookingSerializer},
        tags=['Bookings - Client'],
    )
    def post(self, request):
        serializer = BookingCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        booking = serializer.save(client=request.user, status='pending')

        return success_response(
            data=BookingSerializer(booking).data,
            message="Booking created successfully. Awaiting barber approval.",
            status_code=201,
        )


class ClientBookingListView(generics.ListAPIView):
    """List all bookings for the current client."""
    serializer_class = BookingSerializer
    permission_classes = [IsAuthenticated, IsClient]
    filterset_fields = ['status']
    ordering_fields = ['date', 'created_at']

    @swagger_auto_schema(
        operation_description="List all your bookings with optional status filter.",
        tags=['Bookings - Client'],
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        return Booking.objects.filter(client=self.request.user)


class ClientBookingDetailView(APIView):
    """Get booking details or cancel a booking (client)."""
    permission_classes = [IsAuthenticated, IsClient]

    @swagger_auto_schema(
        operation_description="Get booking details.",
        responses={200: BookingSerializer},
        tags=['Bookings - Client'],
    )
    def get(self, request, pk):
        try:
            booking = Booking.objects.get(pk=pk, client=request.user)
        except Booking.DoesNotExist:
            return error_response("Booking not found.", status_code=404)
        return success_response(data=BookingSerializer(booking).data)

    @swagger_auto_schema(
        operation_description="Cancel a booking.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'reason': openapi.Schema(type=openapi.TYPE_STRING, description='Cancellation reason'),
            },
        ),
        tags=['Bookings - Client'],
    )
    def delete(self, request, pk):
        try:
            booking = Booking.objects.get(pk=pk, client=request.user)
        except Booking.DoesNotExist:
            return error_response("Booking not found.", status_code=404)

        if not booking.can_cancel():
            return error_response(
                "Cannot cancel this booking. It may be too close to the appointment time or already processed.",
                status_code=400,
            )

        booking.status = 'cancelled'
        booking.cancellation_reason = request.data.get('reason', '')
        booking.save(update_fields=['status', 'cancellation_reason', 'updated_at'])

        return success_response(message="Booking cancelled successfully.")


# ==============================================================================
# BOOKING VIEWS (BARBER)
# ==============================================================================
class BarberBookingListView(generics.ListAPIView):
    """List all bookings for the barber's business."""
    serializer_class = BookingSerializer
    permission_classes = [IsAuthenticated, IsBarberOrSubBarber]
    filterset_fields = ['status', 'date']
    ordering_fields = ['date', 'start_time', 'created_at']

    @swagger_auto_schema(
        operation_description="List all bookings for your business.",
        tags=['Bookings - Barber'],
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        user = self.request.user
        if hasattr(user, 'barber_profile'):
            return Booking.objects.filter(barber=user.barber_profile)
        elif hasattr(user, 'employee_profile') and hasattr(user.employee_profile, 'salon'):
            # Salon employees see bookings for their salon
            return Booking.objects.filter(employee=user.employee_profile)
        return Booking.objects.none()


class BarberBookingStatusView(APIView):
    """Update booking status (approve/reject/complete)."""
    permission_classes = [IsAuthenticated, IsBarberOrSubBarber]

    @swagger_auto_schema(
        operation_description="Update a booking's status (approve, reject, complete).",
        request_body=BookingStatusUpdateSerializer,
        tags=['Bookings - Barber'],
    )
    def patch(self, request, pk):
        booking = self._get_booking(request, pk)
        if not booking:
            return error_response("Booking not found.", status_code=404)

        serializer = BookingStatusUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        new_status = serializer.validated_data['status']
        reason = serializer.validated_data.get('reason', '')

        # Validate status transitions
        valid_transitions = {
            'pending': ['approved', 'rejected'],
            'approved': ['completed', 'cancelled'],
        }
        if new_status not in valid_transitions.get(booking.status, []):
            return error_response(
                f"Cannot transition from '{booking.status}' to '{new_status}'.",
                status_code=400,
            )

        booking.status = new_status
        if new_status == 'rejected':
            booking.rejection_reason = reason
        elif new_status == 'cancelled':
            booking.cancellation_reason = reason

        booking.save()

        # Update the business's total bookings on completion.
        # `booking.barber` is null for salon bookings, which can reach this view
        # through the employee branch of _get_booking, so it must be guarded.
        if new_status == 'completed':
            _increment_completed_counter(booking)

        return success_response(
            data=BookingSerializer(booking).data,
            message=f"Booking {new_status} successfully.",
        )

    def _get_booking(self, request, pk):
        try:
            if hasattr(request.user, 'barber_profile'):
                return Booking.objects.get(pk=pk, barber=request.user.barber_profile)
            elif hasattr(request.user, 'employee_profile') and hasattr(request.user.employee_profile, 'salon'):
                return Booking.objects.get(pk=pk, employee=request.user.employee_profile)
        except Booking.DoesNotExist:
            return None
        return None


class BarberBookingRescheduleView(APIView):
    """Reschedule a booking."""
    permission_classes = [IsAuthenticated, IsBarberOrSubBarber]

    @swagger_auto_schema(
        operation_description="Reschedule a booking to a new date/time.",
        request_body=BookingRescheduleSerializer,
        tags=['Bookings - Barber'],
    )
    def post(self, request, pk):
        booking = self._get_booking(request, pk)
        if not booking:
            return error_response("Booking not found.", status_code=404)

        if booking.status not in ('pending', 'approved'):
            return error_response("Only pending or approved bookings can be rescheduled.", status_code=400)

        serializer = BookingRescheduleSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Check for conflicts
        conflicts = Booking.objects.filter(
            barber=booking.barber,
            date=serializer.validated_data['new_date'],
            status__in=['pending', 'approved'],
            start_time__lt=serializer.validated_data['new_end_time'],
            end_time__gt=serializer.validated_data['new_start_time'],
        ).exclude(pk=booking.pk)

        if conflicts.exists():
            return error_response("The new time slot conflicts with another booking.", status_code=400)

        # Mark old booking
        old_booking = booking
        old_booking.status = 'rescheduled'
        old_booking.save(update_fields=['status'])

        # Create new booking
        new_booking = Booking.objects.create(
            client=booking.client,
            barber=booking.barber,
            employee=booking.employee,
            service=booking.service,
            date=serializer.validated_data['new_date'],
            start_time=serializer.validated_data['new_start_time'],
            end_time=serializer.validated_data['new_end_time'],
            notes=booking.notes,
            status='approved',
            rescheduled_from=old_booking,
        )

        return success_response(
            data=BookingSerializer(new_booking).data,
            message="Booking rescheduled successfully.",
        )

    def _get_booking(self, request, pk):
        try:
            if hasattr(request.user, 'barber_profile'):
                return Booking.objects.get(pk=pk, barber=request.user.barber_profile)
            elif hasattr(request.user, 'employee_profile') and hasattr(request.user.employee_profile, 'salon'):
                return Booking.objects.get(pk=pk, employee=request.user.employee_profile)
        except Booking.DoesNotExist:
            return None
        return None


# ==============================================================================
# TIME SLOT / AVAILABILITY VIEWS
# ==============================================================================
class TimeSlotListCreateView(APIView):
    """Manage barber time slots/availability."""
    permission_classes = [IsAuthenticated, IsBarberOrSubBarber]

    @swagger_auto_schema(
        operation_description="List time slots for a specific date.",
        manual_parameters=[
            openapi.Parameter('date', openapi.IN_QUERY, description="Date (YYYY-MM-DD)", type=openapi.TYPE_STRING),
        ],
        responses={200: TimeSlotSerializer(many=True)},
        tags=['Availability'],
    )
    def get(self, request):
        barber_profile = self._get_barber_profile(request)
        if not barber_profile:
            return error_response("Barber profile not found.", status_code=404)

        slots = TimeSlot.objects.filter(barber=barber_profile)
        date = request.query_params.get('date')
        if date:
            slots = slots.filter(date=date)
        serializer = TimeSlotSerializer(slots, many=True)
        return success_response(data=serializer.data)

    @swagger_auto_schema(
        operation_description="Create a new time slot.",
        request_body=TimeSlotCreateSerializer,
        responses={201: TimeSlotSerializer},
        tags=['Availability'],
    )
    def post(self, request):
        barber_profile = self._get_barber_profile(request)
        if not barber_profile:
            return error_response("Barber profile not found.", status_code=404)

        serializer = TimeSlotCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        slot = serializer.save(barber=barber_profile)
        return success_response(
            data=TimeSlotSerializer(slot).data,
            message="Time slot created successfully.",
            status_code=201,
        )

    def _get_barber_profile(self, request):
        if hasattr(request.user, 'barber_profile'):
            return request.user.barber_profile
        return None


class PublicAvailabilityView(generics.ListAPIView):
    """Public view to check a barber's availability."""
    serializer_class = TimeSlotSerializer
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        operation_description="View a barber's available time slots.",
        manual_parameters=[
            openapi.Parameter('date', openapi.IN_QUERY, description="Date (YYYY-MM-DD)", type=openapi.TYPE_STRING),
        ],
        tags=['Barber Search'],
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        barber_id = self.kwargs.get('barber_id')
        qs = TimeSlot.objects.filter(
            barber_id=barber_id,
            is_available=True,
            is_blocked=False,
            date__gte=timezone.now().date(),
        )
        date = self.request.query_params.get('date')
        if date:
            qs = qs.filter(date=date)
        return qs


# ==============================================================================
# SALON: PUBLIC EMPLOYEE AVAILABILITY
# ==============================================================================
class SalonEmployeeAvailabilityView(APIView):
    """Public view of one active salon employee's bookable availability."""
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        operation_description=(
            "View an active salon employee's available time slots. Slots already "
            "taken by a pending or approved booking are excluded."
        ),
        manual_parameters=[
            openapi.Parameter('date', openapi.IN_QUERY, description="Exact date (YYYY-MM-DD)", type=openapi.TYPE_STRING),
            openapi.Parameter('date_from', openapi.IN_QUERY, description="Range start (YYYY-MM-DD)", type=openapi.TYPE_STRING),
            openapi.Parameter('date_to', openapi.IN_QUERY, description="Range end (YYYY-MM-DD)", type=openapi.TYPE_STRING),
        ],
        responses={200: SalonPublicTimeSlotSerializer(many=True)},
        tags=['Salon Search'],
    )
    def get(self, request, employee_id):
        employee = SalonEmployee.objects.filter(
            pk=employee_id,
            is_active=True,
            user__is_active=True,
            salon__user__is_active=True,
        ).first()
        if not employee:
            return error_response("Employee not found.", status_code=404)

        qs = TimeSlot.objects.filter(
            salon_id=employee.salon_id,
            employee=employee,
            is_available=True,
            is_blocked=False,
            date__gte=timezone.now().date(),
        )

        date = request.query_params.get('date')
        date_from = request.query_params.get('date_from')
        date_to = request.query_params.get('date_to')
        if date:
            qs = qs.filter(date=date)
        if date_from:
            qs = qs.filter(date__gte=date_from)
        if date_to:
            qs = qs.filter(date__lte=date_to)

        # Exclude slots already occupied by an active booking for this employee.
        taken = Booking.objects.filter(
            employee=employee,
            status__in=ACTIVE_BOOKING_STATUSES,
            date=OuterRef('date'),
            start_time__lt=OuterRef('end_time'),
            end_time__gt=OuterRef('start_time'),
        )
        qs = qs.exclude(Exists(taken))

        return success_response(data=SalonPublicTimeSlotSerializer(qs, many=True).data)


# ==============================================================================
# SALON: EMPLOYEE AVAILABILITY MANAGEMENT (EMPLOYEE'S OWN SLOTS)
# ==============================================================================
class SalonEmployeeSlotListCreateView(APIView):
    """A salon employee manages their OWN availability."""
    permission_classes = [IsAuthenticated, IsSalonEmployee]

    def _get_employee(self, request):
        return SalonEmployee.objects.filter(user=request.user).first()

    @swagger_auto_schema(
        operation_description="List your own availability slots.",
        manual_parameters=[
            openapi.Parameter('date', openapi.IN_QUERY, description="Exact date (YYYY-MM-DD)", type=openapi.TYPE_STRING),
            openapi.Parameter('date_from', openapi.IN_QUERY, description="Range start", type=openapi.TYPE_STRING),
            openapi.Parameter('date_to', openapi.IN_QUERY, description="Range end", type=openapi.TYPE_STRING),
        ],
        responses={200: SalonTimeSlotSerializer(many=True)},
        tags=['Salon Availability'],
    )
    def get(self, request):
        employee = self._get_employee(request)
        if not employee:
            return error_response("Employee profile not found.", status_code=404)

        qs = TimeSlot.objects.filter(salon_id=employee.salon_id, employee=employee)
        qs = _apply_date_filters(qs, request)
        return success_response(data=SalonTimeSlotSerializer(qs, many=True).data)

    @swagger_auto_schema(
        operation_description="Create one of your own availability slots.",
        request_body=SalonTimeSlotCreateUpdateSerializer,
        responses={201: SalonTimeSlotSerializer},
        tags=['Salon Availability'],
    )
    def post(self, request):
        employee = self._get_employee(request)
        if not employee:
            return error_response("Employee profile not found.", status_code=404)

        serializer = SalonTimeSlotCreateUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        slot = _create_salon_slot(serializer, employee)
        if slot is None:
            return error_response("You already have a slot starting at this time.", status_code=400)
        return success_response(
            data=SalonTimeSlotSerializer(slot).data,
            message="Availability slot created successfully.",
            status_code=201,
        )


class SalonEmployeeSlotDetailView(APIView):
    """A salon employee updates/deletes their OWN availability slot."""
    permission_classes = [IsAuthenticated, IsSalonEmployee]

    def _get_slot(self, request, pk):
        """Tenant-scoped: another employee's slot is simply not found."""
        employee = SalonEmployee.objects.filter(user=request.user).first()
        if not employee:
            return None
        return TimeSlot.objects.filter(
            pk=pk, employee=employee, salon_id=employee.salon_id
        ).first()

    @swagger_auto_schema(
        operation_description="Update one of your own availability slots.",
        request_body=SalonTimeSlotCreateUpdateSerializer,
        tags=['Salon Availability'],
    )
    def patch(self, request, pk):
        slot = self._get_slot(request, pk)
        if not slot:
            return error_response("Time slot not found.", status_code=404)
        serializer = SalonTimeSlotCreateUpdateSerializer(slot, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return success_response(
            data=SalonTimeSlotSerializer(slot).data,
            message="Availability slot updated successfully.",
        )

    @swagger_auto_schema(
        operation_description="Delete one of your own availability slots.",
        tags=['Salon Availability'],
    )
    def delete(self, request, pk):
        slot = self._get_slot(request, pk)
        if not slot:
            return error_response("Time slot not found.", status_code=404)
        slot.delete()
        return success_response(message="Availability slot deleted successfully.")


# ==============================================================================
# SALON: OWNER-SIDE AVAILABILITY MANAGEMENT
# ==============================================================================
class SalonOwnerSlotListCreateView(APIView):
    """A salon owner views/creates availability for employees of their own salon."""
    permission_classes = [IsAuthenticated, IsSalonOwner]

    @swagger_auto_schema(
        operation_description="List availability slots across your salon's employees.",
        manual_parameters=[
            openapi.Parameter('employee', openapi.IN_QUERY, description="Filter by employee id", type=openapi.TYPE_INTEGER),
            openapi.Parameter('date', openapi.IN_QUERY, description="Exact date (YYYY-MM-DD)", type=openapi.TYPE_STRING),
            openapi.Parameter('date_from', openapi.IN_QUERY, description="Range start", type=openapi.TYPE_STRING),
            openapi.Parameter('date_to', openapi.IN_QUERY, description="Range end", type=openapi.TYPE_STRING),
        ],
        responses={200: SalonTimeSlotSerializer(many=True)},
        tags=['Salon Availability'],
    )
    def get(self, request):
        salon = _get_salon_profile(request)
        if not salon:
            return error_response("Salon profile not found. Create one first.", status_code=404)

        qs = TimeSlot.objects.filter(salon=salon)
        employee_id = request.query_params.get('employee')
        if employee_id:
            qs = qs.filter(employee_id=employee_id)
        qs = _apply_date_filters(qs, request)
        return success_response(data=SalonTimeSlotSerializer(qs, many=True).data)

    @swagger_auto_schema(
        operation_description="Create an availability slot for an employee of your salon.",
        request_body=SalonTimeSlotCreateUpdateSerializer,
        manual_parameters=[
            openapi.Parameter('employee', openapi.IN_QUERY, description="Employee id (required)", type=openapi.TYPE_INTEGER),
        ],
        responses={201: SalonTimeSlotSerializer},
        tags=['Salon Availability'],
    )
    def post(self, request):
        salon = _get_salon_profile(request)
        if not salon:
            return error_response("Salon profile not found. Create one first.", status_code=404)

        employee_id = request.data.get('employee') or request.query_params.get('employee')
        if not employee_id:
            return error_response("An employee id is required.", status_code=400)

        # Scoped lookup: an employee of another salon is never found.
        employee = SalonEmployee.objects.filter(pk=employee_id, salon=salon).first()
        if not employee:
            return error_response("Employee not found in your salon.", status_code=404)

        serializer = SalonTimeSlotCreateUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        slot = _create_salon_slot(serializer, employee)
        if slot is None:
            return error_response("This employee already has a slot starting at this time.", status_code=400)
        return success_response(
            data=SalonTimeSlotSerializer(slot).data,
            message="Availability slot created successfully.",
            status_code=201,
        )


class SalonOwnerSlotDetailView(APIView):
    """A salon owner updates/deletes availability slots within their own salon."""
    permission_classes = [IsAuthenticated, IsSalonOwner]

    def _get_slot(self, request, pk):
        salon = _get_salon_profile(request)
        if not salon:
            return None
        return TimeSlot.objects.filter(pk=pk, salon=salon).first()

    @swagger_auto_schema(
        operation_description="Update an availability slot belonging to your salon.",
        request_body=SalonTimeSlotCreateUpdateSerializer,
        tags=['Salon Availability'],
    )
    def patch(self, request, pk):
        slot = self._get_slot(request, pk)
        if not slot:
            return error_response("Time slot not found.", status_code=404)
        serializer = SalonTimeSlotCreateUpdateSerializer(slot, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return success_response(
            data=SalonTimeSlotSerializer(slot).data,
            message="Availability slot updated successfully.",
        )

    @swagger_auto_schema(
        operation_description="Delete an availability slot belonging to your salon.",
        tags=['Salon Availability'],
    )
    def delete(self, request, pk):
        slot = self._get_slot(request, pk)
        if not slot:
            return error_response("Time slot not found.", status_code=404)
        slot.delete()
        return success_response(message="Availability slot deleted successfully.")


# ==============================================================================
# SALON: BOOKING CREATION (CLIENT)
# ==============================================================================
class SalonBookingCreateView(APIView):
    """Create a salon booking (client only)."""
    permission_classes = [IsAuthenticated, IsClient]

    @swagger_auto_schema(
        operation_description=(
            "Create a salon appointment. The client is taken from the "
            "authenticated user. The salon, employee and service are all "
            "re-verified server-side."
        ),
        request_body=SalonBookingCreateSerializer,
        responses={201: BookingSerializer},
        tags=['Bookings - Salon'],
    )
    def post(self, request):
        serializer = SalonBookingCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        booking = serializer.save(client=request.user, status='pending')

        return success_response(
            data=BookingSerializer(booking).data,
            message="Booking created successfully and is awaiting confirmation.",
            status_code=201,
        )


# ==============================================================================
# SALON: EMPLOYEE BOOKING ACCESS
# ==============================================================================
class SalonEmployeeBookingListView(generics.ListAPIView):
    """A salon employee lists ONLY the bookings assigned to them."""
    serializer_class = BookingSerializer
    permission_classes = [IsAuthenticated, IsSalonEmployee]
    filterset_fields = ['status', 'date', 'service']
    ordering_fields = ['date', 'start_time', 'created_at']

    @swagger_auto_schema(
        operation_description=(
            "List bookings assigned to you. Filters: status, date, service, "
            "date_from, date_to."
        ),
        manual_parameters=[
            openapi.Parameter('date_from', openapi.IN_QUERY, description="Range start (YYYY-MM-DD)", type=openapi.TYPE_STRING),
            openapi.Parameter('date_to', openapi.IN_QUERY, description="Range end (YYYY-MM-DD)", type=openapi.TYPE_STRING),
        ],
        tags=['Bookings - Salon'],
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        employee = SalonEmployee.objects.filter(user=self.request.user).first()
        if not employee:
            return Booking.objects.none()
        # Scoped in the database on BOTH employee and salon.
        qs = Booking.objects.filter(
            employee=employee, salon_id=employee.salon_id
        ).select_related('client', 'salon', 'employee__user', 'service')
        return _apply_date_filters(qs, self.request)


class SalonEmployeeBookingDetailView(APIView):
    """A salon employee retrieves ONE booking assigned to them."""
    permission_classes = [IsAuthenticated, IsSalonEmployee]

    @swagger_auto_schema(
        operation_description="Get one booking assigned to you.",
        responses={200: BookingSerializer},
        tags=['Bookings - Salon'],
    )
    def get(self, request, pk):
        booking = _get_employee_booking(request, pk)
        if not booking:
            return error_response("Booking not found.", status_code=404)
        return success_response(data=BookingSerializer(booking).data)


# ==============================================================================
# SALON: OWNER BOOKING ACCESS
# ==============================================================================
class SalonOwnerBookingListView(generics.ListAPIView):
    """A salon owner lists ALL bookings belonging to their salon."""
    serializer_class = BookingSerializer
    permission_classes = [IsAuthenticated, IsSalonOwner]
    filterset_fields = ['status', 'date', 'employee', 'service']
    search_fields = ['client__full_name', 'client__email']
    ordering_fields = ['date', 'start_time', 'created_at']

    @swagger_auto_schema(
        operation_description=(
            "List every booking for your salon, across all employees. Filters: "
            "status, date, employee, service, date_from, date_to, search."
        ),
        manual_parameters=[
            openapi.Parameter('date_from', openapi.IN_QUERY, description="Range start (YYYY-MM-DD)", type=openapi.TYPE_STRING),
            openapi.Parameter('date_to', openapi.IN_QUERY, description="Range end (YYYY-MM-DD)", type=openapi.TYPE_STRING),
        ],
        tags=['Bookings - Salon'],
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        salon = _get_salon_profile(self.request)
        if not salon:
            return Booking.objects.none()
        # Scoped in the database on the owner's salon.
        qs = Booking.objects.filter(salon=salon).select_related(
            'client', 'salon', 'employee__user', 'service'
        )
        return _apply_date_filters(qs, self.request)


class SalonOwnerBookingDetailView(APIView):
    """A salon owner retrieves ONE booking belonging to their salon."""
    permission_classes = [IsAuthenticated, IsSalonOwner]

    @swagger_auto_schema(
        operation_description="Get one booking belonging to your salon.",
        responses={200: BookingSerializer},
        tags=['Bookings - Salon'],
    )
    def get(self, request, pk):
        salon = _get_salon_profile(request)
        if not salon:
            return error_response("Salon profile not found.", status_code=404)
        booking = Booking.objects.filter(pk=pk, salon=salon).first()
        if not booking:
            return error_response("Booking not found.", status_code=404)
        return success_response(data=BookingSerializer(booking).data)


# ==============================================================================
# SALON: BOOKING STATUS MANAGEMENT
# ==============================================================================
class SalonBookingStatusView(APIView):
    """
    Update a salon booking's status.

    A salon owner may manage any booking of their salon; an employee may manage
    only the bookings assigned to them.
    """
    permission_classes = [IsAuthenticated, IsSalonOrEmployee]

    @swagger_auto_schema(
        operation_description="Update a salon booking's status (approve, reject, complete, cancel).",
        request_body=BookingStatusUpdateSerializer,
        responses={200: BookingSerializer},
        tags=['Bookings - Salon'],
    )
    def patch(self, request, pk):
        booking = _get_salon_manageable_booking(request, pk)
        if not booking:
            return error_response("Booking not found.", status_code=404)

        serializer = BookingStatusUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        new_status = serializer.validated_data['status']
        reason = serializer.validated_data.get('reason', '')

        if new_status not in VALID_STATUS_TRANSITIONS.get(booking.status, []):
            return error_response(
                f"Cannot transition from '{booking.status}' to '{new_status}'.",
                status_code=400,
            )

        booking.status = new_status
        if new_status == 'rejected':
            booking.rejection_reason = reason
        elif new_status == 'cancelled':
            booking.cancellation_reason = reason

        booking.save()

        if new_status == 'completed':
            # Salon bookings have barber=None; this credits the employee.
            _increment_completed_counter(booking)

        return success_response(
            data=BookingSerializer(booking).data,
            message=f"Booking {new_status} successfully.",
        )


# ==============================================================================
# SALON: BOOKING RESCHEDULE
# ==============================================================================
class SalonBookingRescheduleView(APIView):
    """
    Reschedule a salon booking.

    Never touches `Booking.barber`. Validates the employee's availability and
    employee-level conflicts for the new window.
    """
    permission_classes = [IsAuthenticated, IsSalonOrEmployee]

    @swagger_auto_schema(
        operation_description="Reschedule a salon booking to a new date/time.",
        request_body=BookingRescheduleSerializer,
        responses={200: BookingSerializer},
        tags=['Bookings - Salon'],
    )
    def post(self, request, pk):
        booking = _get_salon_manageable_booking(request, pk)
        if not booking:
            return error_response("Booking not found.", status_code=404)

        if booking.status not in ('pending', 'approved'):
            return error_response("Only pending or approved bookings can be rescheduled.", status_code=400)

        serializer = BookingRescheduleSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        new_date = serializer.validated_data['new_date']
        new_start = serializer.validated_data['new_start_time']
        new_end = serializer.validated_data['new_end_time']
        employee = booking.employee

        if not employee:
            return error_response("This salon booking has no assigned employee.", status_code=400)

        # Service eligibility still has to hold for the same employee.
        if booking.service and not employee_can_provide(booking.service, employee):
            return error_response(
                "The assigned employee no longer provides this service.", status_code=400
            )

        if not employee_has_availability(employee, new_date, new_start, new_end):
            return error_response(
                "The employee is not available at the requested time.", status_code=400
            )

        if employee_conflicting_bookings(
            employee, new_date, new_start, new_end, exclude_pk=booking.pk
        ).exists():
            return error_response(
                "The new time slot conflicts with another booking for this employee.",
                status_code=400,
            )

        with transaction.atomic():
            old_booking = booking
            old_booking.status = 'rescheduled'
            old_booking.save(update_fields=['status'])

            new_booking = Booking.objects.create(
                client=old_booking.client,
                barber=None,
                salon=old_booking.salon,
                employee=old_booking.employee,
                service=old_booking.service,
                date=new_date,
                start_time=new_start,
                end_time=new_end,
                notes=old_booking.notes,
                status='approved',
                rescheduled_from=old_booking,
            )

        return success_response(
            data=BookingSerializer(new_booking).data,
            message="Booking rescheduled successfully.",
        )
