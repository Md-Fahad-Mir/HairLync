from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from drf_yasg.utils import swagger_auto_schema

from .models import Favorite
from .serializers import FavoriteSerializer, FavoriteCreateSerializer
from Apps.users.permissions import IsClient
from Apps.users.utils import success_response, error_response
from Apps.profiles.models import BarberProfile


class FavoriteListView(APIView):
    """List all favorite barbers for the current client."""
    permission_classes = [IsAuthenticated, IsClient]

    @swagger_auto_schema(
        operation_description="List all your favorite/saved barbers.",
        responses={200: FavoriteSerializer(many=True)},
        tags=['Favorites'],
    )
    def get(self, request):
        favorites = Favorite.objects.filter(client=request.user).select_related(
            'barber', 'barber__user'
        )
        serializer = FavoriteSerializer(favorites, many=True)
        return success_response(data=serializer.data)


class FavoriteToggleView(APIView):
    """Add or remove a barber from favorites."""
    permission_classes = [IsAuthenticated, IsClient]

    @swagger_auto_schema(
        operation_description="Add a barber to your favorites.",
        request_body=FavoriteCreateSerializer,
        tags=['Favorites'],
    )
    def post(self, request):
        serializer = FavoriteCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        barber_id = serializer.validated_data['barber_id']

        try:
            barber_profile = BarberProfile.objects.get(pk=barber_id)
        except BarberProfile.DoesNotExist:
            return error_response("Barber not found.", status_code=404)

        favorite, created = Favorite.objects.get_or_create(
            client=request.user,
            barber=barber_profile,
        )

        if created:
            return success_response(
                data=FavoriteSerializer(favorite).data,
                message="Barber added to favorites.",
                status_code=201,
            )
        else:
            favorite.delete()
            return success_response(message="Barber removed from favorites.")
