from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.utils import timezone
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from .models import Booking, TimeSlot
from .serializers import (
    BookingSerializer, BookingCreateSerializer,
    BookingStatusUpdateSerializer, BookingRescheduleSerializer,
    TimeSlotSerializer, TimeSlotCreateSerializer,
)
from Apps.users.permissions import IsClient, IsBarber, IsBarberOrSubBarber
from Apps.users.utils import success_response, error_response
from Apps.profiles.models import BarberProfile


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
        elif hasattr(user, 'employee_profile'):
            return Booking.objects.filter(barber=user.employee_profile.barber)
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

        # Update barber's total bookings on completion
        if new_status == 'completed':
            barber_profile = booking.barber
            barber_profile.total_bookings += 1
            barber_profile.save(update_fields=['total_bookings'])

        return success_response(
            data=BookingSerializer(booking).data,
            message=f"Booking {new_status} successfully.",
        )

    def _get_booking(self, request, pk):
        try:
            if hasattr(request.user, 'barber_profile'):
                return Booking.objects.get(pk=pk, barber=request.user.barber_profile)
            elif hasattr(request.user, 'employee_profile'):
                return Booking.objects.get(pk=pk, barber=request.user.employee_profile.barber)
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
            elif hasattr(request.user, 'employee_profile'):
                return Booking.objects.get(pk=pk, barber=request.user.employee_profile.barber)
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
        elif hasattr(request.user, 'employee_profile'):
            return request.user.employee_profile.barber
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
