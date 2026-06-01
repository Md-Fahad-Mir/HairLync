from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.contrib.auth import get_user_model
from django.db.models import Q
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from .models import ClientProfile, BarberProfile, EmployeeProfile
from .serializers import (
    ClientProfileSerializer, ClientProfileUpdateSerializer,
    BarberProfileSerializer, BarberProfileUpdateSerializer, BarberProfileListSerializer,
    EmployeeProfileSerializer, EmployeeCreateSerializer,
)
from Apps.users.permissions import IsClient, IsBarber, IsSubscribedBarber, IsAdminUser
from Apps.users.utils import success_response, error_response

User = get_user_model()


# ==============================================================================
# CLIENT PROFILE VIEWS
# ==============================================================================
class ClientProfileView(APIView):
    """Get or create/update the client's profile."""
    permission_classes = [IsAuthenticated, IsClient]

    @swagger_auto_schema(
        operation_description="Get the current client's profile.",
        responses={200: ClientProfileSerializer},
        tags=['Client Profile'],
    )
    def get(self, request):
        profile, created = ClientProfile.objects.get_or_create(user=request.user)
        serializer = ClientProfileSerializer(profile)
        return success_response(data=serializer.data)

    @swagger_auto_schema(
        operation_description="Update the current client's profile.",
        request_body=ClientProfileUpdateSerializer,
        responses={200: ClientProfileSerializer},
        tags=['Client Profile'],
    )
    def patch(self, request):
        profile, created = ClientProfile.objects.get_or_create(user=request.user)
        serializer = ClientProfileUpdateSerializer(profile, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return success_response(
            data=ClientProfileSerializer(profile).data,
            message="Profile updated successfully.",
        )


# ==============================================================================
# BARBER PROFILE VIEWS
# ==============================================================================
class BarberProfileView(APIView):
    """Get or create/update the barber's business profile."""
    permission_classes = [IsAuthenticated, IsBarber]

    @swagger_auto_schema(
        operation_description="Get the current barber's business profile.",
        responses={200: BarberProfileSerializer},
        tags=['Barber Profile'],
    )
    def get(self, request):
        try:
            profile = BarberProfile.objects.get(user=request.user)
        except BarberProfile.DoesNotExist:
            return error_response("Barber profile not found. Create one first.", status_code=404)
        serializer = BarberProfileSerializer(profile)
        return success_response(data=serializer.data)

    @swagger_auto_schema(
        operation_description="Create or update the barber's business profile.",
        request_body=BarberProfileUpdateSerializer,
        responses={200: BarberProfileSerializer},
        tags=['Barber Profile'],
    )
    def post(self, request):
        profile, created = BarberProfile.objects.get_or_create(
            user=request.user,
            defaults={'business_name': request.data.get('business_name', request.user.full_name)}
        )
        serializer = BarberProfileUpdateSerializer(profile, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        msg = "Profile created successfully." if created else "Profile updated successfully."
        return success_response(data=BarberProfileSerializer(profile).data, message=msg)

    @swagger_auto_schema(
        operation_description="Update the barber's business profile.",
        request_body=BarberProfileUpdateSerializer,
        responses={200: BarberProfileSerializer},
        tags=['Barber Profile'],
    )
    def patch(self, request):
        try:
            profile = BarberProfile.objects.get(user=request.user)
        except BarberProfile.DoesNotExist:
            return error_response("Barber profile not found.", status_code=404)
        serializer = BarberProfileUpdateSerializer(profile, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return success_response(
            data=BarberProfileSerializer(profile).data,
            message="Profile updated successfully.",
        )


class BarberProfileDetailView(generics.RetrieveAPIView):
    """Public view to see a barber's profile."""
    serializer_class = BarberProfileSerializer
    permission_classes = [AllowAny]
    lookup_field = 'pk'

    @swagger_auto_schema(
        operation_description="View a barber's public profile.",
        tags=['Barber Search'],
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        return BarberProfile.objects.filter(is_verified=True, user__is_active=True)


class BarberSearchView(generics.ListAPIView):
    """Search and filter barbers (public)."""
    serializer_class = BarberProfileListSerializer
    permission_classes = [AllowAny]
    filterset_fields = ['category', 'city', 'is_verified', 'is_accepting_clients']
    search_fields = ['business_name', 'city', 'user__full_name']
    ordering_fields = ['average_rating', 'total_reviews', 'experience_years', 'created_at']

    @swagger_auto_schema(
        operation_description="Search for barbers by location, category, rating, etc.",
        manual_parameters=[
            openapi.Parameter('search', openapi.IN_QUERY, description="Search by name or city", type=openapi.TYPE_STRING),
            openapi.Parameter('category', openapi.IN_QUERY, description="Filter by category", type=openapi.TYPE_STRING),
            openapi.Parameter('city', openapi.IN_QUERY, description="Filter by city", type=openapi.TYPE_STRING),
            openapi.Parameter('min_rating', openapi.IN_QUERY, description="Minimum rating", type=openapi.TYPE_NUMBER),
            openapi.Parameter('ordering', openapi.IN_QUERY, description="Order by field", type=openapi.TYPE_STRING),
        ],
        tags=['Barber Search'],
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        qs = BarberProfile.objects.filter(user__is_active=True)
        min_rating = self.request.query_params.get('min_rating')
        if min_rating:
            try:
                qs = qs.filter(average_rating__gte=float(min_rating))
            except (ValueError, TypeError):
                pass
        return qs


# ==============================================================================
# EMPLOYEE MANAGEMENT VIEWS
# ==============================================================================
class EmployeeListCreateView(APIView):
    """List and create employees for a barber business."""
    permission_classes = [IsAuthenticated, IsBarber]

    @swagger_auto_schema(
        operation_description="List all employees under the current barber's business.",
        responses={200: EmployeeProfileSerializer(many=True)},
        tags=['Employee Management'],
    )
    def get(self, request):
        try:
            barber_profile = request.user.barber_profile
        except BarberProfile.DoesNotExist:
            return error_response("Barber profile not found.", status_code=404)

        employees = EmployeeProfile.objects.filter(barber=barber_profile)
        serializer = EmployeeProfileSerializer(employees, many=True)
        return success_response(data=serializer.data)

    @swagger_auto_schema(
        operation_description="Add a new employee to the barber's business.",
        request_body=EmployeeCreateSerializer,
        responses={201: EmployeeProfileSerializer},
        tags=['Employee Management'],
    )
    def post(self, request):
        serializer = EmployeeCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            barber_profile = request.user.barber_profile
        except BarberProfile.DoesNotExist:
            return error_response("Barber profile not found.", status_code=404)

        email = serializer.validated_data['email']

        if User.objects.filter(email=email).exists():
            return error_response("A user with this email already exists.", status_code=400)

        # Create employee user
        employee_user = User.objects.create_user(
            email=email,
            password=serializer.validated_data['password'],
            full_name=serializer.validated_data['full_name'],
            role='barber',
            is_active=True,
            is_verified=True,
        )

        # Create employee profile
        employee = EmployeeProfile.objects.create(
            barber=barber_profile,
            user=employee_user,
            position=serializer.validated_data.get('position', 'Stylist'),
            can_manage_bookings=serializer.validated_data.get('can_manage_bookings', True),
            can_manage_schedule=serializer.validated_data.get('can_manage_schedule', True),
            can_access_tools=serializer.validated_data.get('can_access_tools', True),
        )

        return success_response(
            data=EmployeeProfileSerializer(employee).data,
            message="Employee added successfully.",
            status_code=201,
        )


class EmployeeDetailView(APIView):
    """Get, update, or delete a specific employee."""
    permission_classes = [IsAuthenticated, IsBarber]

    @swagger_auto_schema(
        operation_description="Get employee details.",
        responses={200: EmployeeProfileSerializer},
        tags=['Employee Management'],
    )
    def get(self, request, pk):
        employee = self._get_employee(request, pk)
        if not employee:
            return error_response("Employee not found.", status_code=404)
        return success_response(data=EmployeeProfileSerializer(employee).data)

    @swagger_auto_schema(
        operation_description="Update employee details.",
        request_body=EmployeeProfileSerializer,
        tags=['Employee Management'],
    )
    def patch(self, request, pk):
        employee = self._get_employee(request, pk)
        if not employee:
            return error_response("Employee not found.", status_code=404)
        serializer = EmployeeProfileSerializer(employee, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return success_response(
            data=EmployeeProfileSerializer(employee).data,
            message="Employee updated successfully.",
        )

    @swagger_auto_schema(
        operation_description="Remove an employee.",
        tags=['Employee Management'],
    )
    def delete(self, request, pk):
        employee = self._get_employee(request, pk)
        if not employee:
            return error_response("Employee not found.", status_code=404)
        employee_user = employee.user
        employee.delete()
        employee_user.is_active = False
        employee_user.save(update_fields=['is_active'])
        return success_response(message="Employee removed successfully.")

    def _get_employee(self, request, pk):
        try:
            barber_profile = request.user.barber_profile
            return EmployeeProfile.objects.get(pk=pk, barber=barber_profile)
        except (BarberProfile.DoesNotExist, EmployeeProfile.DoesNotExist):
            return None
