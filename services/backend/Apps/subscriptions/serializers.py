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
            'user', 'status', 'start_date', 'end_date',
            'cancelled_at', 'created_at', 'updated_at',
        ]

    def get_is_active(self, obj):
        return obj.is_active_subscription


class SubscriptionCreateSerializer(serializers.Serializer):
    plan_id = serializers.IntegerField()
    payment_reference = serializers.CharField(max_length=255, required=False, default='')
    payment_method = serializers.CharField(max_length=50, required=False, default='manual')
