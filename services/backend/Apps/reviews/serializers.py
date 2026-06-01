from rest_framework import serializers
from .models import Review


class ReviewSerializer(serializers.ModelSerializer):
    client_name = serializers.CharField(source='client.full_name', read_only=True)
    barber_name = serializers.CharField(source='barber.business_name', read_only=True)

    class Meta:
        model = Review
        fields = '__all__'
        read_only_fields = [
            'client', 'barber_response', 'barber_responded_at',
            'is_approved', 'is_flagged', 'flag_reason',
            'created_at', 'updated_at',
        ]


class ReviewCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ['barber', 'booking', 'rating', 'comment']


class ReviewResponseSerializer(serializers.Serializer):
    response = serializers.CharField(max_length=2000)


class ReviewModerationSerializer(serializers.Serializer):
    is_approved = serializers.BooleanField(required=False)
    is_flagged = serializers.BooleanField(required=False)
    flag_reason = serializers.CharField(required=False, default='')
