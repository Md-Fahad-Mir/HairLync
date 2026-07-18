from rest_framework import serializers
from .models import SubscriptionPlan, Subscription


class SubscriptionPlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubscriptionPlan
        fields = '__all__'
        read_only_fields = ['created_at']


class SubscriptionSerializer(serializers.ModelSerializer):
    plan_details = SubscriptionPlanSerializer(source='plan', read_only=True)
    is_active = serializers.SerializerMethodField()

    class Meta:
        model = Subscription
        fields = '__all__'
        read_only_fields = [
            'user', 'status', 'platform', 'start_date', 'end_date',
            'stripe_customer_id', 'stripe_subscription_id', 'stripe_checkout_session_id',
            'last_payment_error', 'payment_failed_at',
            'cancelled_at', 'created_at', 'updated_at',
        ]

    def get_is_active(self, obj):
        return obj.is_active_subscription


class SubscriptionCreateSerializer(serializers.Serializer):
    """Admin/internal-only: manually create + activate a subscription for a
    barber without going through a real payment provider. `user_id` targets
    the barber to grant access to; omit it to target the requesting admin's
    own account (rare in practice — this endpoint is for internal use)."""
    plan_id = serializers.IntegerField()
    user_id = serializers.IntegerField(required=False)
    payment_reference = serializers.CharField(max_length=255, required=False, default='')
    payment_method = serializers.CharField(max_length=50, required=False, default='manual')


class StripeCheckoutSerializer(serializers.Serializer):
    """Request body for POST /stripe/checkout/. Only an internal plan_id is
    accepted — price and product are always resolved server-side from the
    database, never trusted from the client."""
    plan_id = serializers.IntegerField()
