from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.contrib.auth import get_user_model
from django.db.models import (
    Q, ExpressionWrapper, F, FloatField, Func, Value,
)
import math
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from .models import ClientProfile, BarberProfile, SalonProfile, SalonEmployee
from .serializers import (
    ClientProfileSerializer, ClientProfileUpdateSerializer,
    BarberProfileSerializer, BarberProfileUpdateSerializer, BarberProfileListSerializer,
    BarberProfileNearbySerializer,
    SalonProfileSerializer, SalonProfileUpdateSerializer, SalonProfileListSerializer,
    SalonProfileNearbySerializer,
    SalonEmployeeSerializer, SalonEmployeePublicSerializer,
    SalonEmployeeCreateSerializer, SalonEmployeeUpdateSerializer,
)
from Apps.users.permissions import (
    IsClient, IsBarber, IsSubscribedBarber, IsAdminUser,
    IsSalon, IsSalonOwner, IsSalonEmployee, IsSalonOrEmployee,
)
from Apps.users.utils import success_response, error_response

User = get_user_model()


# ------------------------------------------------------------------------------
# Haversine distance annotation (database-level, no Python loop)
# ------------------------------------------------------------------------------
def _haversine_qs(qs, client_lat, client_lon, radius_km=10):
    """
    Annotate *qs* with ``distance_km`` using a pure-SQL Haversine expression
    and return only rows within *radius_km*, ordered nearest first.

    Works on both SQLite (math functions available since SQLite 3.x) and
    PostgreSQL without requiring PostGIS.

    Formula:
        a  = sin²(Δlat/2) + cos(lat1)·cos(lat2)·sin²(Δlon/2)
        km = 2 · R · asin(√a)   where R = 6371 km
    """
    R = 6371.0  # Earth radius in km

    lat1_rad = math.radians(float(client_lat))
    lon1_rad = math.radians(float(client_lon))

    # Annotate barber/salon lat & lon as floats (DecimalField → float cast)
    qs = qs.annotate(
        _lat2=ExpressionWrapper(F('latitude'), output_field=FloatField()),
        _lon2=ExpressionWrapper(F('longitude'), output_field=FloatField()),
    )

    # Convert provider lat/lon to radians
    qs = qs.annotate(
        _lat2_rad=ExpressionWrapper(
            F('_lat2') * Value(math.pi / 180.0),
            output_field=FloatField(),
        ),
        _lon2_rad=ExpressionWrapper(
            F('_lon2') * Value(math.pi / 180.0),
            output_field=FloatField(),
        ),
    )

    # Δlat and Δlon in radians
    qs = qs.annotate(
        _dlat=ExpressionWrapper(
            F('_lat2_rad') - Value(lat1_rad),
            output_field=FloatField(),
        ),
        _dlon=ExpressionWrapper(
            F('_lon2_rad') - Value(lon1_rad),
            output_field=FloatField(),
        ),
    )

    # sin²(Δlat/2)
    qs = qs.annotate(
        _sin_dlat=ExpressionWrapper(
            Func(F('_dlat') * Value(0.5), function='SIN', output_field=FloatField()),
            output_field=FloatField(),
        ),
    )
    qs = qs.annotate(
        _a_lat=ExpressionWrapper(
            F('_sin_dlat') * F('_sin_dlat'),
            output_field=FloatField(),
        ),
    )

    # sin²(Δlon/2)
    qs = qs.annotate(
        _sin_dlon=ExpressionWrapper(
            Func(F('_dlon') * Value(0.5), function='SIN', output_field=FloatField()),
            output_field=FloatField(),
        ),
    )
    qs = qs.annotate(
        _a_lon=ExpressionWrapper(
            F('_sin_dlon') * F('_sin_dlon'),
            output_field=FloatField(),
        ),
    )

    # cos(lat1) · cos(lat2)
    qs = qs.annotate(
        _cos_lat2=ExpressionWrapper(
            Func(F('_lat2_rad'), function='COS', output_field=FloatField()),
            output_field=FloatField(),
        ),
        _cos_lat1=Value(math.cos(lat1_rad), output_field=FloatField()),
    )

    # a  = sin²(Δlat/2) + cos(lat1)·cos(lat2)·sin²(Δlon/2)
    qs = qs.annotate(
        _a=ExpressionWrapper(
            F('_a_lat') + F('_cos_lat1') * F('_cos_lat2') * F('_a_lon'),
            output_field=FloatField(),
        ),
    )

    # c = 2 · asin(√a)  → distance_km = R · c
    qs = qs.annotate(
        _sqrt_a=ExpressionWrapper(
            Func(F('_a'), function='SQRT', output_field=FloatField()),
            output_field=FloatField(),
        ),
    )
    qs = qs.annotate(
        distance_km=ExpressionWrapper(
            Value(2.0 * R) * Func(F('_sqrt_a'), function='ASIN', output_field=FloatField()),
            output_field=FloatField(),
        ),
    )

    # Filter within radius and order nearest first
    qs = qs.filter(distance_km__lte=radius_km).order_by('distance_km')
    return qs



# ==============================================================================
# CLIENT PROFILE VIEWS
# ==============================================================================
class ClientProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        if self.request.method in ["PUT", "PATCH", "POST"]:
            return [IsAuthenticated(), IsClient()]
        return [IsAuthenticated()]
        
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

class ClientProfileListView(generics.ListAPIView):
    """
    List all active client profiles and allow filtering/searching.
    Can search by client profile ID, user ID, email, or full name.
    """
    queryset = ClientProfile.objects.filter(user__is_active=True)
    serializer_class = ClientProfileSerializer
    permission_classes = [IsAuthenticated]  # Or AllowAny, depending on security requirements

    # Use django-filter fields for exact matches (like ID)
    filterset_fields = ['id', 'user__id']
    
    # Use search fields for text queries (like full name or email)
    search_fields = ['user__full_name', 'user__email']

    @swagger_auto_schema(
        operation_description="List client profiles. Filter by 'id' or 'user__id' query parameters.",
        manual_parameters=[
            openapi.Parameter('id', openapi.IN_QUERY, description="Filter by client profile ID", type=openapi.TYPE_INTEGER),
            openapi.Parameter('user__id', openapi.IN_QUERY, description="Filter by user account ID", type=openapi.TYPE_INTEGER),
            openapi.Parameter('search', openapi.IN_QUERY, description="Search by email or name", type=openapi.TYPE_STRING),
        ],
        tags=['Client Profile Search'],
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class ClientProfileDetailView(generics.RetrieveAPIView):
    """Public view to see a client's profile."""
    serializer_class = ClientProfileSerializer
    permission_classes = [AllowAny]
    lookup_field = "pk"

    @swagger_auto_schema(
        operation_description="View a client's public profile.",
        tags=["Client"],
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        return ClientProfile.objects.filter(user__is_active=True)
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
        return BarberProfile.objects.filter(user__is_active=True)


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
# SALON PROFILE VIEWS
# ==============================================================================
class SalonProfileView(APIView):
    """Get or create/update the salon's business profile."""
    permission_classes = [IsAuthenticated, IsSalonOwner]

    @swagger_auto_schema(
        operation_description="Get the current salon's business profile.",
        responses={200: SalonProfileSerializer},
        tags=['Salon Profile'],
    )
    def get(self, request):
        try:
            profile = SalonProfile.objects.get(user=request.user)
        except SalonProfile.DoesNotExist:
            return error_response("Salon profile not found. Create one first.", status_code=404)
        serializer = SalonProfileSerializer(profile)
        return success_response(data=serializer.data)

    @swagger_auto_schema(
        operation_description="Create or update the salon's business profile.",
        request_body=SalonProfileUpdateSerializer,
        responses={200: SalonProfileSerializer},
        tags=['Salon Profile'],
    )
    def post(self, request):
        profile, created = SalonProfile.objects.get_or_create(
            user=request.user,
            defaults={'business_name': request.data.get('business_name', request.user.full_name)}
        )
        serializer = SalonProfileUpdateSerializer(profile, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        msg = "Salon profile created successfully." if created else "Salon profile updated successfully."
        return success_response(data=SalonProfileSerializer(profile).data, message=msg)

    @swagger_auto_schema(
        operation_description="Update the salon's business profile.",
        request_body=SalonProfileUpdateSerializer,
        responses={200: SalonProfileSerializer},
        tags=['Salon Profile'],
    )
    def patch(self, request):
        try:
            profile = SalonProfile.objects.get(user=request.user)
        except SalonProfile.DoesNotExist:
            return error_response("Salon profile not found.", status_code=404)
        serializer = SalonProfileUpdateSerializer(profile, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return success_response(
            data=SalonProfileSerializer(profile).data,
            message="Salon profile updated successfully.",
        )


class SalonProfileDetailView(generics.RetrieveAPIView):
    """Public view to see a salon's profile (includes employees)."""
    serializer_class = SalonProfileSerializer
    permission_classes = [AllowAny]
    lookup_field = 'pk'

    @swagger_auto_schema(
        operation_description="View a salon's public profile with employee list.",
        tags=['Salon Search'],
    )
    def get(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = SalonProfileSerializer(instance)
        data = serializer.data

        # Include public employee info ("Our Professionals" section)
        employees = SalonEmployee.objects.filter(salon=instance, is_active=True)
        data['professionals'] = SalonEmployeePublicSerializer(employees, many=True).data

        return success_response(data=data)

    def get_queryset(self):
        return SalonProfile.objects.filter(user__is_active=True)


class SalonSearchView(generics.ListAPIView):
    """Search and filter salons (public)."""
    serializer_class = SalonProfileListSerializer
    permission_classes = [AllowAny]
    filterset_fields = ['city', 'is_verified', 'is_accepting_clients']
    search_fields = ['business_name', 'city', 'user__full_name']
    ordering_fields = ['average_rating', 'total_reviews', 'experience_years', 'created_at']

    @swagger_auto_schema(
        operation_description="Search for salons by location, rating, etc.",
        manual_parameters=[
            openapi.Parameter('search', openapi.IN_QUERY, description="Search by name or city", type=openapi.TYPE_STRING),
            openapi.Parameter('city', openapi.IN_QUERY, description="Filter by city", type=openapi.TYPE_STRING),
            openapi.Parameter('min_rating', openapi.IN_QUERY, description="Minimum rating", type=openapi.TYPE_NUMBER),
            openapi.Parameter('ordering', openapi.IN_QUERY, description="Order by field", type=openapi.TYPE_STRING),
        ],
        tags=['Salon Search'],
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        qs = SalonProfile.objects.filter(user__is_active=True)
        min_rating = self.request.query_params.get('min_rating')
        if min_rating:
            try:
                qs = qs.filter(average_rating__gte=float(min_rating))
            except (ValueError, TypeError):
                pass
        return qs


# ==============================================================================
# SALON EMPLOYEE (SUB-PROFILE) MANAGEMENT VIEWS
# ==============================================================================
class SalonEmployeeListCreateView(APIView):
    """
    List and create employees for a salon business.
    Only the salon OWNER can create employees (sub-profiles).
    """
    permission_classes = [IsAuthenticated, IsSalonOwner]

    @swagger_auto_schema(
        operation_description="List all employees under the current salon.",
        responses={200: SalonEmployeeSerializer(many=True)},
        tags=['Salon Employee Management'],
    )
    def get(self, request):
        try:
            salon_profile = request.user.salon_profile
        except SalonProfile.DoesNotExist:
            return error_response("Salon profile not found. Create one first.", status_code=404)

        employees = SalonEmployee.objects.filter(salon=salon_profile)
        serializer = SalonEmployeeSerializer(employees, many=True)
        return success_response(data=serializer.data)

    @swagger_auto_schema(
        operation_description=(
            "Add a new employee to the salon. Only requires full_name. "
            "Email and password are auto-generated. "
            "Format: email=firstname+lastname+2digits@hairlync.app, "
            "password=8 random chars."
        ),
        request_body=SalonEmployeeCreateSerializer,
        responses={201: SalonEmployeeSerializer},
        tags=['Salon Employee Management'],
    )
    def post(self, request):
        serializer = SalonEmployeeCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            salon_profile = request.user.salon_profile
        except SalonProfile.DoesNotExist:
            return error_response("Salon profile not found. Create one first.", status_code=404)

        full_name = serializer.validated_data['full_name']
        name_parts = full_name.split()
        first_name = name_parts[0]
        last_name = ' '.join(name_parts[1:]) if len(name_parts) > 1 else ''

        # Auto-generate credentials
        generated_email = SalonEmployee.generate_employee_email(first_name, last_name)
        generated_password = SalonEmployee.generate_employee_password()

        # Create the sub-profile user account
        employee_user = User.objects.create_user(
            email=generated_email,
            password=generated_password,
            full_name=full_name,
            role='salon',
            is_active=True,
            is_verified=True,
            is_sub_profile=True,
            parent_salon=request.user,
        )

        # Create the employee profile
        employee = SalonEmployee.objects.create(
            salon=salon_profile,
            user=employee_user,
            generated_email=generated_email,
            generated_password=generated_password,
            position=serializer.validated_data.get('position', 'Hair Stylist'),
            role_title=serializer.validated_data.get('role_title', 'Hair Stylist'),
        )

        return success_response(
            data=SalonEmployeeSerializer(employee).data,
            message="Employee added successfully.",
            status_code=201,
        )


class SalonEmployeeDetailView(APIView):
    """
    Get, update, or delete a specific salon employee.
    Only the salon OWNER can manage employees.
    """
    permission_classes = [IsAuthenticated, IsSalonOwner]

    @swagger_auto_schema(
        operation_description="Get employee details (includes generated credentials).",
        responses={200: SalonEmployeeSerializer},
        tags=['Salon Employee Management'],
    )
    def get(self, request, pk):
        employee = self._get_employee(request, pk)
        if not employee:
            return error_response("Employee not found.", status_code=404)
        return success_response(data=SalonEmployeeSerializer(employee).data)

    @swagger_auto_schema(
        operation_description="Update employee details.",
        request_body=SalonEmployeeUpdateSerializer,
        tags=['Salon Employee Management'],
    )
    def patch(self, request, pk):
        employee = self._get_employee(request, pk)
        if not employee:
            return error_response("Employee not found.", status_code=404)
        serializer = SalonEmployeeUpdateSerializer(employee, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return success_response(
            data=SalonEmployeeSerializer(employee).data,
            message="Employee updated successfully.",
        )

    @swagger_auto_schema(
        operation_description="Remove an employee. Deactivates their user account.",
        tags=['Salon Employee Management'],
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
            salon_profile = request.user.salon_profile
            return SalonEmployee.objects.get(pk=pk, salon=salon_profile)
        except (SalonProfile.DoesNotExist, SalonEmployee.DoesNotExist):
            return None


class SalonEmployeeSelfProfileView(APIView):
    """
    Allow salon employee (sub-profile) to view and update their OWN profile.
    They cannot access other employees' profiles or the salon owner's profile.
    """
    permission_classes = [IsAuthenticated, IsSalonEmployee]

    @swagger_auto_schema(
        operation_description="Get the current employee's own profile.",
        responses={200: SalonEmployeeSerializer},
        tags=['Salon Employee Self'],
    )
    def get(self, request):
        try:
            employee = SalonEmployee.objects.get(user=request.user)
        except SalonEmployee.DoesNotExist:
            return error_response("Employee profile not found.", status_code=404)
        serializer = SalonEmployeeSerializer(employee)
        return success_response(data=serializer.data)

    @swagger_auto_schema(
        operation_description="Update the current employee's own profile.",
        request_body=SalonEmployeeUpdateSerializer,
        tags=['Salon Employee Self'],
    )
    def patch(self, request):
        try:
            employee = SalonEmployee.objects.get(user=request.user)
        except SalonEmployee.DoesNotExist:
            return error_response("Employee profile not found.", status_code=404)
        serializer = SalonEmployeeUpdateSerializer(employee, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return success_response(
            data=SalonEmployeeSerializer(employee).data,
            message="Profile updated successfully.",
        )


# ==============================================================================
# NEARBY BARBER & SALON VIEWS
# ==============================================================================
class BarberNearbyView(generics.ListAPIView):
    """
    Return barbers within 10 km of the authenticated client's saved location,
    sorted from nearest to farthest.

    Requires the client to have saved ``latitude`` and ``longitude`` on their
    ``ClientProfile``.  Barbers without valid coordinates are excluded.
    The ``distance_km`` field in each result is calculated entirely in the
    database using the Haversine formula — no Python-level iteration.
    """
    serializer_class = BarberProfileNearbySerializer
    permission_classes = [IsAuthenticated]
    # Preserve existing filter/search/ordering backends from global settings
    filterset_fields = ['category', 'city', 'is_verified', 'is_accepting_clients']
    search_fields = ['business_name', 'city', 'user__full_name']

    @swagger_auto_schema(
        operation_description=(
            "List barbers within 10 km of the client's saved location, "
            "sorted nearest to farthest. Requires the client to have set "
            "latitude & longitude on their profile. "
            "Returns distance_km rounded to 2 decimal places."
        ),
        manual_parameters=[
            openapi.Parameter(
                'category', openapi.IN_QUERY,
                description="Filter by category (barber/hairdresser/stylist…)",
                type=openapi.TYPE_STRING,
            ),
            openapi.Parameter(
                'city', openapi.IN_QUERY,
                description="Filter by city",
                type=openapi.TYPE_STRING,
            ),
            openapi.Parameter(
                'search', openapi.IN_QUERY,
                description="Search by business name or owner name",
                type=openapi.TYPE_STRING,
            ),
        ],
        tags=['Nearby'],
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        # Resolve client location
        try:
            client_profile = ClientProfile.objects.get(user=self.request.user)
        except ClientProfile.DoesNotExist:
            return BarberProfile.objects.none()

        client_lat = client_profile.latitude
        client_lon = client_profile.longitude

        if client_lat is None or client_lon is None:
            return BarberProfile.objects.none()

        # Base queryset: active barbers with valid coordinates
        qs = BarberProfile.objects.filter(
            user__is_active=True,
            latitude__isnull=False,
            longitude__isnull=False,
        ).select_related('user')

        return _haversine_qs(qs, client_lat, client_lon, radius_km=10)


class SalonNearbyView(generics.ListAPIView):
    """
    Return salons within 10 km of the authenticated client's saved location,
    sorted from nearest to farthest.

    Requires the client to have saved ``latitude`` and ``longitude`` on their
    ``ClientProfile``.  Salons without valid coordinates are excluded.
    The ``distance_km`` field in each result is calculated entirely in the
    database using the Haversine formula — no Python-level iteration.
    """
    serializer_class = SalonProfileNearbySerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['city', 'is_verified', 'is_accepting_clients']
    search_fields = ['business_name', 'city', 'user__full_name']

    @swagger_auto_schema(
        operation_description=(
            "List salons within 10 km of the client's saved location, "
            "sorted nearest to farthest. Requires the client to have set "
            "latitude & longitude on their profile. "
            "Returns distance_km rounded to 2 decimal places."
        ),
        manual_parameters=[
            openapi.Parameter(
                'city', openapi.IN_QUERY,
                description="Filter by city",
                type=openapi.TYPE_STRING,
            ),
            openapi.Parameter(
                'search', openapi.IN_QUERY,
                description="Search by business name or owner name",
                type=openapi.TYPE_STRING,
            ),
        ],
        tags=['Nearby'],
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        # Resolve client location
        try:
            client_profile = ClientProfile.objects.get(user=self.request.user)
        except ClientProfile.DoesNotExist:
            return SalonProfile.objects.none()

        client_lat = client_profile.latitude
        client_lon = client_profile.longitude

        if client_lat is None or client_lon is None:
            return SalonProfile.objects.none()

        # Base queryset: active salons with valid coordinates
        qs = SalonProfile.objects.filter(
            user__is_active=True,
            latitude__isnull=False,
            longitude__isnull=False,
        ).select_related('user')

        return _haversine_qs(qs, client_lat, client_lon, radius_km=10)
