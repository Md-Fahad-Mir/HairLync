from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from drf_yasg.utils import swagger_auto_schema

from .models import EducationCategory, EducationalContent
from .serializers import (
    EducationCategorySerializer,
    EducationalContentSerializer,
    EducationalContentListSerializer,
)
from Apps.users.permissions import IsBarber, IsSubscribedBarber, IsAdminUser
from Apps.users.utils import success_response, error_response


class EducationCategoryListView(generics.ListAPIView):
    """List all education categories."""
    serializer_class = EducationCategorySerializer
    permission_classes = [AllowAny]
    queryset = EducationCategory.objects.all()

    @swagger_auto_schema(
        operation_description="List all educational content categories.",
        tags=['Education'],
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class EducationalContentListView(generics.ListAPIView):
    """List educational content (professionals only for premium)."""
    serializer_class = EducationalContentListSerializer
    permission_classes = [IsAuthenticated, IsBarber]
    filterset_fields = ['content_type', 'difficulty', 'is_premium']
    search_fields = ['title', 'description']
    ordering_fields = ['created_at', 'view_count']

    @swagger_auto_schema(
        operation_description="List all educational content. Premium content requires subscription.",
        tags=['Education'],
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        qs = EducationalContent.objects.filter(is_published=True)
        # If user doesn't have subscription, only show free content
        if not self.request.user.is_subscribed():
            qs = qs.filter(is_premium=False)
        return qs


class EducationalContentDetailView(APIView):
    """View a single educational content item."""
    permission_classes = [IsAuthenticated, IsBarber]

    @swagger_auto_schema(
        operation_description="View educational content details.",
        responses={200: EducationalContentSerializer},
        tags=['Education'],
    )
    def get(self, request, slug):
        try:
            content = EducationalContent.objects.get(slug=slug, is_published=True)
        except EducationalContent.DoesNotExist:
            return error_response("Content not found.", status_code=404)

        # Check premium access
        if content.is_premium and not request.user.is_subscribed():
            return error_response(
                "This content requires an active subscription.",
                status_code=403,
            )

        # Increment view count
        content.view_count += 1
        content.save(update_fields=['view_count'])

        return success_response(data=EducationalContentSerializer(content).data)


class EducationalContentAdminView(APIView):
    """Create educational content (admin only)."""
    permission_classes = [IsAdminUser]

    @swagger_auto_schema(
        operation_description="Create new educational content (admin only).",
        request_body=EducationalContentSerializer,
        tags=['Admin'],
    )
    def post(self, request):
        serializer = EducationalContentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        content = serializer.save(author=request.user)
        return success_response(
            data=EducationalContentSerializer(content).data,
            message="Educational content created successfully.",
            status_code=201,
        )
