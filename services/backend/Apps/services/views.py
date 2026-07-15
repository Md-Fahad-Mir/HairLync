from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from .models import ServiceCategory, Service
from .serializers import (
    ServiceCategorySerializer, ServiceSerializer, ServiceCreateSerializer,
    SalonServiceSerializer, SalonServicePublicSerializer,
    SalonServiceCreateUpdateSerializer,
)
from Apps.users.permissions import (
    IsBarber, IsSubscribedBarber, IsAdminUser, IsSalonOwner,
)
from Apps.users.utils import success_response, error_response
from Apps.profiles.models import BarberProfile, SalonProfile


# ==============================================================================
# SERVICE CATEGORY VIEWS
# ==============================================================================
class ServiceCategoryListView(generics.ListAPIView):
    """List all service categories (public)."""
    serializer_class = ServiceCategorySerializer
    permission_classes = [AllowAny]
    queryset = ServiceCategory.objects.all()
    search_fields = ['name']

    @swagger_auto_schema(
        operation_description="List all available service categories.",
        tags=['Services'],
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class ServiceCategoryAdminView(generics.CreateAPIView):
    """Create a service category (admin only)."""
    serializer_class = ServiceCategorySerializer
    permission_classes = [IsAdminUser]
    queryset = ServiceCategory.objects.all()

    @swagger_auto_schema(
        operation_description="Create a new service category (admin only).",
        tags=['Admin'],
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


# ==============================================================================
# SERVICE VIEWS
# ==============================================================================
class BarberServiceListCreateView(APIView):
    """List and create services for the current barber."""
    permission_classes = [IsAuthenticated, IsBarber]

    @swagger_auto_schema(
        operation_description="List all services for the current barber.",
        responses={200: ServiceSerializer(many=True)},
        tags=['Services'],
    )
    def get(self, request):
        try:
            barber_profile = request.user.barber_profile
        except BarberProfile.DoesNotExist:
            return error_response("Barber profile not found.", status_code=404)

        services = Service.objects.filter(barber=barber_profile)
        serializer = ServiceSerializer(services, many=True)
        return success_response(data=serializer.data)

    @swagger_auto_schema(
        operation_description="Create a new service for the current barber.",
        request_body=ServiceCreateSerializer,
        responses={201: ServiceSerializer},
        tags=['Services'],
    )
    def post(self, request):
        try:
            barber_profile = request.user.barber_profile
        except BarberProfile.DoesNotExist:
            return error_response("Barber profile not found.", status_code=404)

        serializer = ServiceCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        service = serializer.save(barber=barber_profile)
        return success_response(
            data=ServiceSerializer(service).data,
            message="Service created successfully.",
            status_code=201,
        )


class BarberServiceDetailView(APIView):
    """Update or delete a barber's service."""
    permission_classes = [IsAuthenticated, IsBarber]

    @swagger_auto_schema(
        operation_description="Update a service.",
        request_body=ServiceCreateSerializer,
        tags=['Services'],
    )
    def patch(self, request, pk):
        service = self._get_service(request, pk)
        if not service:
            return error_response("Service not found.", status_code=404)
        serializer = ServiceCreateSerializer(service, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return success_response(
            data=ServiceSerializer(service).data,
            message="Service updated successfully.",
        )

    @swagger_auto_schema(
        operation_description="Delete a service.",
        tags=['Services'],
    )
    def delete(self, request, pk):
        service = self._get_service(request, pk)
        if not service:
            return error_response("Service not found.", status_code=404)
        service.delete()
        return success_response(message="Service deleted successfully.")

    def _get_service(self, request, pk):
        try:
            return Service.objects.get(pk=pk, barber=request.user.barber_profile)
        except (Service.DoesNotExist, BarberProfile.DoesNotExist):
            return None


class BarberServicesPublicView(generics.ListAPIView):
    """Public view to see a barber's services."""
    serializer_class = ServiceSerializer
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        operation_description="View a barber's services (public).",
        tags=['Barber Search'],
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        barber_id = self.kwargs.get('barber_id')
        return Service.objects.filter(barber_id=barber_id, is_active=True)


# ==============================================================================
# SALON SERVICE VIEWS (SALON OWNER ONLY)
# ==============================================================================
class SalonServicesPublicView(generics.ListAPIView):
    """Public view to see a salon's active services."""
    serializer_class = SalonServicePublicSerializer
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        operation_description="View a salon's active services (public).",
        tags=['Salon Search'],
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        salon_id = self.kwargs.get('salon_id')
        return Service.objects.filter(
            salon_id=salon_id,
            is_active=True,
            salon__user__is_active=True,
        ).prefetch_related('available_employees')


class SalonServiceListCreateView(APIView):
    """List and create services for the authenticated salon owner."""
    permission_classes = [IsAuthenticated, IsSalonOwner]

    def _get_salon(self, request):
        try:
            return request.user.salon_profile
        except SalonProfile.DoesNotExist:
            return None

    @swagger_auto_schema(
        operation_description="List all services owned by the current salon.",
        responses={200: SalonServiceSerializer(many=True)},
        tags=['Salon Services'],
    )
    def get(self, request):
        salon = self._get_salon(request)
        if not salon:
            return error_response("Salon profile not found. Create one first.", status_code=404)

        services = Service.objects.filter(salon=salon).prefetch_related('available_employees')
        return success_response(data=SalonServiceSerializer(services, many=True).data)

    @swagger_auto_schema(
        operation_description=(
            "Create a service owned by the current salon. The salon is taken from "
            "the authenticated user. Optionally restrict it to specific employees "
            "via `available_employees`; leave empty to allow all active employees."
        ),
        request_body=SalonServiceCreateUpdateSerializer,
        responses={201: SalonServiceSerializer},
        tags=['Salon Services'],
    )
    def post(self, request):
        salon = self._get_salon(request)
        if not salon:
            return error_response("Salon profile not found. Create one first.", status_code=404)

        serializer = SalonServiceCreateUpdateSerializer(
            data=request.data, context={'salon': salon, 'request': request}
        )
        serializer.is_valid(raise_exception=True)
        service = serializer.save(salon=salon, barber=None)
        return success_response(
            data=SalonServiceSerializer(service).data,
            message="Salon service created successfully.",
            status_code=201,
        )


class SalonServiceDetailView(APIView):
    """Retrieve, update or delete one service owned by the authenticated salon."""
    permission_classes = [IsAuthenticated, IsSalonOwner]

    def _get_service(self, request, pk):
        """Tenant-scoped lookup: another salon's service is simply not found."""
        try:
            salon = request.user.salon_profile
        except SalonProfile.DoesNotExist:
            return None
        return Service.objects.filter(pk=pk, salon=salon).first()

    @swagger_auto_schema(
        operation_description="Get one of the current salon's services.",
        responses={200: SalonServiceSerializer},
        tags=['Salon Services'],
    )
    def get(self, request, pk):
        service = self._get_service(request, pk)
        if not service:
            return error_response("Service not found.", status_code=404)
        return success_response(data=SalonServiceSerializer(service).data)

    @swagger_auto_schema(
        operation_description="Update one of the current salon's services (including activate/deactivate via `is_active`).",
        request_body=SalonServiceCreateUpdateSerializer,
        tags=['Salon Services'],
    )
    def patch(self, request, pk):
        service = self._get_service(request, pk)
        if not service:
            return error_response("Service not found.", status_code=404)

        serializer = SalonServiceCreateUpdateSerializer(
            service, data=request.data, partial=True,
            context={'salon': service.salon, 'request': request},
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return success_response(
            data=SalonServiceSerializer(service).data,
            message="Salon service updated successfully.",
        )

    @swagger_auto_schema(
        operation_description=(
            "Delete one of the current salon's services. A service that is "
            "referenced by pending or approved bookings is deactivated instead "
            "of deleted, to preserve booking history."
        ),
        tags=['Salon Services'],
    )
    def delete(self, request, pk):
        service = self._get_service(request, pk)
        if not service:
            return error_response("Service not found.", status_code=404)

        # Deleting is only safe when no live booking depends on it. Booking.service
        # is SET_NULL, so a hard delete would silently strip history.
        if service.bookings.filter(status__in=('pending', 'approved')).exists():
            service.is_active = False
            service.save(update_fields=['is_active', 'updated_at'])
            return success_response(
                data=SalonServiceSerializer(service).data,
                message=(
                    "Service has active bookings and was deactivated instead of "
                    "deleted."
                ),
            )

        service.delete()
        return success_response(message="Salon service deleted successfully.")
