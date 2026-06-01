from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from drf_yasg.utils import swagger_auto_schema

from .models import SubscriptionPlan, Subscription
from .serializers import SubscriptionPlanSerializer, SubscriptionSerializer, SubscriptionCreateSerializer
from Apps.users.permissions import IsBarber, IsAdminUser
from Apps.users.utils import success_response, error_response


class SubscriptionPlanListView(generics.ListAPIView):
    """List all available subscription plans (public)."""
    serializer_class = SubscriptionPlanSerializer
    permission_classes = [AllowAny]
    queryset = SubscriptionPlan.objects.filter(is_active=True)

    @swagger_auto_schema(
        operation_description="List all available subscription plans.",
        tags=['Subscriptions'],
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class SubscriptionPlanAdminView(generics.CreateAPIView):
    """Create a subscription plan (admin only)."""
    serializer_class = SubscriptionPlanSerializer
    permission_classes = [IsAdminUser]
    queryset = SubscriptionPlan.objects.all()

    @swagger_auto_schema(
        operation_description="Create a new subscription plan (admin only).",
        tags=['Admin'],
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class SubscriptionCreateView(APIView):
    """Subscribe to a plan (barber only)."""
    permission_classes = [IsAuthenticated, IsBarber]

    @swagger_auto_schema(
        operation_description="Subscribe to a plan. Payment integration ready.",
        request_body=SubscriptionCreateSerializer,
        responses={201: SubscriptionSerializer},
        tags=['Subscriptions'],
    )
    def post(self, request):
        serializer = SubscriptionCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        plan_id = serializer.validated_data['plan_id']

        try:
            plan = SubscriptionPlan.objects.get(pk=plan_id, is_active=True)
        except SubscriptionPlan.DoesNotExist:
            return error_response("Subscription plan not found.", status_code=404)

        # Check for existing active subscription
        active_sub = Subscription.objects.filter(
            user=request.user, status='active'
        ).first()
        if active_sub and active_sub.is_active_subscription:
            return error_response("You already have an active subscription.", status_code=400)

        subscription = Subscription.objects.create(
            user=request.user,
            plan=plan,
            payment_reference=serializer.validated_data.get('payment_reference', ''),
            payment_method=serializer.validated_data.get('payment_method', 'manual'),
            amount_paid=plan.price,
        )

        # Auto-activate (in production, this would happen after payment confirmation)
        subscription.activate()

        return success_response(
            data=SubscriptionSerializer(subscription).data,
            message="Subscription activated successfully.",
            status_code=201,
        )


class SubscriptionDetailView(APIView):
    """Get current subscription details or cancel."""
    permission_classes = [IsAuthenticated, IsBarber]

    @swagger_auto_schema(
        operation_description="Get your current subscription details.",
        responses={200: SubscriptionSerializer},
        tags=['Subscriptions'],
    )
    def get(self, request):
        subscription = Subscription.objects.filter(
            user=request.user
        ).order_by('-created_at').first()

        if not subscription:
            return error_response("No subscription found.", status_code=404)

        return success_response(data=SubscriptionSerializer(subscription).data)

    @swagger_auto_schema(
        operation_description="Cancel your current subscription.",
        tags=['Subscriptions'],
    )
    def delete(self, request):
        subscription = Subscription.objects.filter(
            user=request.user, status='active'
        ).first()

        if not subscription:
            return error_response("No active subscription found.", status_code=404)

        subscription.cancel()
        return success_response(message="Subscription cancelled. You will retain access until the end of the billing period.")


class SubscriptionHistoryView(generics.ListAPIView):
    """View subscription history."""
    serializer_class = SubscriptionSerializer
    permission_classes = [IsAuthenticated, IsBarber]

    @swagger_auto_schema(
        operation_description="View your subscription history.",
        tags=['Subscriptions'],
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        return Subscription.objects.filter(user=self.request.user)
