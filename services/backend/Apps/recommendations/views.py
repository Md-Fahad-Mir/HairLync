from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from drf_yasg.utils import swagger_auto_schema

from .models import HairStyleCategory, ClientImage, StyleRecommendation
from .serializers import (
    HairStyleCategorySerializer, ClientImageSerializer,
    StyleRecommendationSerializer, StyleRecommendationCreateSerializer,
)
from Apps.users.permissions import IsBarber, IsSubscribedBarber, IsClient
from Apps.users.utils import success_response, error_response
from Apps.profiles.models import BarberProfile


class HairStyleCategoryListView(generics.ListAPIView):
    """List all hairstyle categories (public)."""
    serializer_class = HairStyleCategorySerializer
    permission_classes = [AllowAny]
    queryset = HairStyleCategory.objects.all()
    filterset_fields = ['occasion']

    @swagger_auto_schema(
        operation_description="List all hairstyle categories by occasion.",
        tags=['Recommendations'],
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class ClientImageUploadView(APIView):
    """Upload a client image for recommendation processing."""
    permission_classes = [IsAuthenticated, IsBarber]

    @swagger_auto_schema(
        operation_description="Upload a client image for AI recommendation preparation.",
        request_body=ClientImageSerializer,
        responses={201: ClientImageSerializer},
        tags=['Recommendations'],
    )
    def post(self, request):
        try:
            barber_profile = request.user.barber_profile
        except BarberProfile.DoesNotExist:
            return error_response("Barber profile not found.", status_code=404)

        serializer = ClientImageSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        image = serializer.save(barber=barber_profile)
        return success_response(
            data=ClientImageSerializer(image).data,
            message="Image uploaded successfully.",
            status_code=201,
        )


class StyleRecommendationCreateView(APIView):
    """Create a style recommendation for a client."""
    permission_classes = [IsAuthenticated, IsBarber]

    @swagger_auto_schema(
        operation_description="Create a hairstyle/treatment recommendation for a client.",
        request_body=StyleRecommendationCreateSerializer,
        responses={201: StyleRecommendationSerializer},
        tags=['Recommendations'],
    )
    def post(self, request):
        try:
            barber_profile = request.user.barber_profile
        except BarberProfile.DoesNotExist:
            return error_response("Barber profile not found.", status_code=404)

        serializer = StyleRecommendationCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        rec = serializer.save(barber=barber_profile)
        return success_response(
            data=StyleRecommendationSerializer(rec).data,
            message="Recommendation created successfully.",
            status_code=201,
        )


class ClientRecommendationsView(generics.ListAPIView):
    """View recommendations received by the current client."""
    serializer_class = StyleRecommendationSerializer
    permission_classes = [IsAuthenticated, IsClient]

    @swagger_auto_schema(
        operation_description="View all hairstyle recommendations you've received.",
        tags=['Recommendations'],
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        return StyleRecommendation.objects.filter(client=self.request.user)


class BarberRecommendationsView(generics.ListAPIView):
    """View recommendations created by the current barber."""
    serializer_class = StyleRecommendationSerializer
    permission_classes = [IsAuthenticated, IsBarber]

    @swagger_auto_schema(
        operation_description="View all recommendations you've created.",
        tags=['Recommendations'],
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        try:
            return StyleRecommendation.objects.filter(barber=self.request.user.barber_profile)
        except BarberProfile.DoesNotExist:
            return StyleRecommendation.objects.none()
