from rest_framework import serializers
from .models import PortfolioItem


class PortfolioItemSerializer(serializers.ModelSerializer):
    barber_name = serializers.CharField(source='barber.business_name', read_only=True)

    class Meta:
        model = PortfolioItem
        fields = '__all__'
        read_only_fields = ['barber', 'created_at', 'updated_at']


class PortfolioItemCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = PortfolioItem
        exclude = ['barber', 'created_at', 'updated_at']
