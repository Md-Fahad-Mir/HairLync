from rest_framework import serializers
from .models import PortfolioItem


class PortfolioItemSerializer(serializers.ModelSerializer):
    owner_name = serializers.CharField(source='get_owner_name', read_only=True)

    class Meta:
        model = PortfolioItem
        fields = '__all__'
        read_only_fields = ['barber', 'salon', 'salon_employee', 'created_at', 'updated_at']


class PortfolioItemCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = PortfolioItem
        exclude = ['barber', 'salon', 'salon_employee', 'created_at', 'updated_at']
