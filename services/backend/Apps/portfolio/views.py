from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from drf_yasg.utils import swagger_auto_schema

from .models import PortfolioItem
from .serializers import PortfolioItemSerializer, PortfolioItemCreateSerializer
from Apps.users.permissions import IsBarber, IsSalon, IsSalonOrEmployee
from Apps.users.utils import success_response, error_response
from Apps.profiles.models import BarberProfile, SalonProfile, SalonEmployee


class BarberPortfolioListCreateView(APIView):
    """List and create portfolio items for the current barber."""
    permission_classes = [IsAuthenticated, IsBarber]

    @swagger_auto_schema(
        operation_description="List all your portfolio items.",
        responses={200: PortfolioItemSerializer(many=True)},
        tags=['Portfolio'],
    )
    def get(self, request):
        try:
            barber_profile = request.user.barber_profile
        except BarberProfile.DoesNotExist:
            return error_response("Barber profile not found.", status_code=404)

        items = PortfolioItem.objects.filter(barber=barber_profile)
        serializer = PortfolioItemSerializer(items, many=True)
        return success_response(data=serializer.data)

    @swagger_auto_schema(
        operation_description="Add a new portfolio item.",
        request_body=PortfolioItemCreateSerializer,
        responses={201: PortfolioItemSerializer},
        tags=['Portfolio'],
    )
    def post(self, request):
        try:
            barber_profile = request.user.barber_profile
        except BarberProfile.DoesNotExist:
            return error_response("Barber profile not found.", status_code=404)

        serializer = PortfolioItemCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        item = serializer.save(barber=barber_profile, owner_type='barber')
        return success_response(
            data=PortfolioItemSerializer(item).data,
            message="Portfolio item added successfully.",
            status_code=201,
        )


class SalonPortfolioListCreateView(APIView):
    """List and create portfolio items for the current salon."""
    permission_classes = [IsAuthenticated, IsSalon]

    @swagger_auto_schema(
        operation_description="List all your salon's portfolio items.",
        responses={200: PortfolioItemSerializer(many=True)},
        tags=['Portfolio'],
    )
    def get(self, request):
        try:
            salon_profile = request.user.salon_profile
        except (SalonProfile.DoesNotExist, AttributeError):
            return error_response("Salon profile not found.", status_code=404)

        items = PortfolioItem.objects.filter(salon=salon_profile)
        serializer = PortfolioItemSerializer(items, many=True)
        return success_response(data=serializer.data)

    @swagger_auto_schema(
        operation_description="Add a new portfolio item to your salon.",
        request_body=PortfolioItemCreateSerializer,
        responses={201: PortfolioItemSerializer},
        tags=['Portfolio'],
    )
    def post(self, request):
        try:
            salon_profile = request.user.salon_profile
        except (SalonProfile.DoesNotExist, AttributeError):
            return error_response("Salon profile not found.", status_code=404)

        serializer = PortfolioItemCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        item = serializer.save(salon=salon_profile, owner_type='salon')
        return success_response(
            data=PortfolioItemSerializer(item).data,
            message="Portfolio item added successfully.",
            status_code=201,
        )


class SalonEmployeePortfolioListCreateView(APIView):
    """List and create portfolio items for a salon employee."""
    permission_classes = [IsAuthenticated, IsSalonOrEmployee]

    @swagger_auto_schema(
        operation_description="List all your portfolio items as a salon employee.",
        responses={200: PortfolioItemSerializer(many=True)},
        tags=['Portfolio'],
    )
    def get(self, request):
        try:
            employee = request.user.employee_profile
        except (SalonEmployee.DoesNotExist, AttributeError):
            return error_response("Employee profile not found.", status_code=404)

        items = PortfolioItem.objects.filter(salon_employee=employee)
        serializer = PortfolioItemSerializer(items, many=True)
        return success_response(data=serializer.data)

    @swagger_auto_schema(
        operation_description="Add a new portfolio item as a salon employee.",
        request_body=PortfolioItemCreateSerializer,
        responses={201: PortfolioItemSerializer},
        tags=['Portfolio'],
    )
    def post(self, request):
        try:
            employee = request.user.employee_profile
        except (SalonEmployee.DoesNotExist, AttributeError):
            return error_response("Employee profile not found.", status_code=404)

        serializer = PortfolioItemCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        item = serializer.save(salon_employee=employee, owner_type='salon_employee')
        return success_response(
            data=PortfolioItemSerializer(item).data,
            message="Portfolio item added successfully.",
            status_code=201,
        )


class PortfolioDetailView(APIView):
    """Update or delete a portfolio item."""
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Update a portfolio item.",
        request_body=PortfolioItemCreateSerializer,
        tags=['Portfolio'],
    )
    def patch(self, request, pk):
        item = self._get_item(request, pk)
        if not item:
            return error_response("Portfolio item not found.", status_code=404)
        serializer = PortfolioItemCreateSerializer(item, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return success_response(
            data=PortfolioItemSerializer(item).data,
            message="Portfolio item updated.",
        )

    @swagger_auto_schema(
        operation_description="Delete a portfolio item.",
        tags=['Portfolio'],
    )
    def delete(self, request, pk):
        item = self._get_item(request, pk)
        if not item:
            return error_response("Portfolio item not found.", status_code=404)
        item.delete()
        return success_response(message="Portfolio item deleted.")

    def _get_item(self, request, pk):
        """Get portfolio item if it belongs to the current user."""
        try:
            item = PortfolioItem.objects.get(pk=pk)
            # Check ownership based on owner type
            if item.owner_type == 'barber':
                if hasattr(request.user, 'barber_profile') and item.barber == request.user.barber_profile:
                    return item
            elif item.owner_type == 'salon':
                if hasattr(request.user, 'salon_profile') and item.salon == request.user.salon_profile:
                    return item
            elif item.owner_type == 'salon_employee':
                if hasattr(request.user, 'employee_profile') and item.salon_employee == request.user.employee_profile:
                    return item
            return None
        except PortfolioItem.DoesNotExist:
            return None


class BarberPortfolioPublicView(generics.ListAPIView):
    """Public view of a barber's portfolio."""
    serializer_class = PortfolioItemSerializer
    permission_classes = [AllowAny]
    filterset_fields = ['category']

    @swagger_auto_schema(
        operation_description="View a barber's portfolio (public).",
        tags=['Barber Search'],
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        barber_id = self.kwargs.get('barber_id')
        return PortfolioItem.objects.filter(barber_id=barber_id, owner_type='barber')


class SalonPortfolioPublicView(generics.ListAPIView):
    """Public view of a salon's portfolio."""
    serializer_class = PortfolioItemSerializer
    permission_classes = [AllowAny]
    filterset_fields = ['category']

    @swagger_auto_schema(
        operation_description="View a salon's portfolio (public).",
        tags=['Salon Search'],
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        salon_id = self.kwargs.get('salon_id')
        return PortfolioItem.objects.filter(salon_id=salon_id, owner_type='salon')


class SalonEmployeePortfolioPublicView(generics.ListAPIView):
    """Public view of a salon employee's portfolio."""
    serializer_class = PortfolioItemSerializer
    permission_classes = [AllowAny]
    filterset_fields = ['category']

    @swagger_auto_schema(
        operation_description="View a salon employee's portfolio (public).",
        tags=['Salon Search'],
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        employee_id = self.kwargs.get('employee_id')
        return PortfolioItem.objects.filter(salon_employee_id=employee_id, owner_type='salon_employee')
