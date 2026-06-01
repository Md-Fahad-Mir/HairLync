from rest_framework import serializers
from .models import HairStyleCategory, ClientImage, StyleRecommendation


class HairStyleCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = HairStyleCategory
        fields = '__all__'
        read_only_fields = ['created_at']


class ClientImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClientImage
        fields = '__all__'
        read_only_fields = ['barber', 'created_at']


class StyleRecommendationSerializer(serializers.ModelSerializer):
    barber_name = serializers.CharField(source='barber.business_name', read_only=True)
    client_name = serializers.CharField(source='client.full_name', read_only=True)

    class Meta:
        model = StyleRecommendation
        fields = '__all__'
        read_only_fields = ['barber', 'created_at']


class StyleRecommendationCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = StyleRecommendation
        exclude = ['barber', 'created_at']
