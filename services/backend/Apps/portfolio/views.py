from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from drf_yasg.utils import swagger_auto_schema

from .models import PortfolioItem
from .serializers import PortfolioItemSerializer, PortfolioItemCreateSerializer
from Apps.users.permissions import IsBarber
from Apps.users.utils import success_response, error_response
from Apps.profiles.models import BarberProfile


class PortfolioListCreateView(APIView):
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
        item = serializer.save(barber=barber_profile)
        return success_response(
            data=PortfolioItemSerializer(item).data,
            message="Portfolio item added successfully.",
            status_code=201,
        )


class PortfolioDetailView(APIView):
    """Update or delete a portfolio item."""
    permission_classes = [IsAuthenticated, IsBarber]

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
        try:
            return PortfolioItem.objects.get(pk=pk, barber=request.user.barber_profile)
        except (PortfolioItem.DoesNotExist, BarberProfile.DoesNotExist):
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
        return PortfolioItem.objects.filter(barber_id=barber_id)
