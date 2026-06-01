from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.utils import timezone
from drf_yasg.utils import swagger_auto_schema

from .models import Review
from .serializers import (
    ReviewSerializer, ReviewCreateSerializer,
    ReviewResponseSerializer, ReviewModerationSerializer,
)
from Apps.users.permissions import IsClient, IsBarber, IsAdminUser
from Apps.users.utils import success_response, error_response
from Apps.profiles.models import BarberProfile


class ReviewCreateView(APIView):
    """Create a review for a barber (client only)."""
    permission_classes = [IsAuthenticated, IsClient]

    @swagger_auto_schema(
        operation_description="Create a review for a barber. Must have a completed booking.",
        request_body=ReviewCreateSerializer,
        responses={201: ReviewSerializer},
        tags=['Reviews'],
    )
    def post(self, request):
        serializer = ReviewCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        barber = serializer.validated_data['barber']
        booking = serializer.validated_data.get('booking')

        # Verify the booking belongs to this client and is completed
        if booking:
            if booking.client != request.user:
                return error_response("This booking does not belong to you.", status_code=400)
            if booking.status != 'completed':
                return error_response("You can only review completed bookings.", status_code=400)

        # Check for existing review
        if Review.objects.filter(client=request.user, barber=barber, booking=booking).exists():
            return error_response("You have already reviewed this booking.", status_code=400)

        review = serializer.save(client=request.user)
        return success_response(
            data=ReviewSerializer(review).data,
            message="Review submitted successfully.",
            status_code=201,
        )


class BarberReviewListView(generics.ListAPIView):
    """List reviews for a barber (public)."""
    serializer_class = ReviewSerializer
    permission_classes = [AllowAny]
    ordering_fields = ['created_at', 'rating']

    @swagger_auto_schema(
        operation_description="View all reviews for a barber.",
        tags=['Reviews'],
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        barber_id = self.kwargs.get('barber_id')
        return Review.objects.filter(barber_id=barber_id, is_approved=True)


class BarberReviewResponseView(APIView):
    """Barber responds to a review."""
    permission_classes = [IsAuthenticated, IsBarber]

    @swagger_auto_schema(
        operation_description="Respond to a client's review.",
        request_body=ReviewResponseSerializer,
        tags=['Reviews'],
    )
    def post(self, request, pk):
        try:
            review = Review.objects.get(pk=pk, barber=request.user.barber_profile)
        except (Review.DoesNotExist, BarberProfile.DoesNotExist):
            return error_response("Review not found.", status_code=404)

        serializer = ReviewResponseSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        review.barber_response = serializer.validated_data['response']
        review.barber_responded_at = timezone.now()
        review.save(update_fields=['barber_response', 'barber_responded_at'])

        return success_response(
            data=ReviewSerializer(review).data,
            message="Response submitted successfully.",
        )


class ReviewModerationView(APIView):
    """Moderate reviews (admin only)."""
    permission_classes = [IsAdminUser]

    @swagger_auto_schema(
        operation_description="Moderate a review (approve/flag).",
        request_body=ReviewModerationSerializer,
        tags=['Admin'],
    )
    def patch(self, request, pk):
        try:
            review = Review.objects.get(pk=pk)
        except Review.DoesNotExist:
            return error_response("Review not found.", status_code=404)

        serializer = ReviewModerationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        update_fields = []
        if 'is_approved' in serializer.validated_data:
            review.is_approved = serializer.validated_data['is_approved']
            update_fields.append('is_approved')
        if 'is_flagged' in serializer.validated_data:
            review.is_flagged = serializer.validated_data['is_flagged']
            update_fields.append('is_flagged')
        if 'flag_reason' in serializer.validated_data:
            review.flag_reason = serializer.validated_data['flag_reason']
            update_fields.append('flag_reason')

        if update_fields:
            review.save(update_fields=update_fields)

        return success_response(
            data=ReviewSerializer(review).data,
            message="Review moderated successfully.",
        )
