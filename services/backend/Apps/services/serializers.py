from rest_framework import serializers
from .models import ServiceCategory, Service


class ServiceCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceCategory
        fields = '__all__'
        read_only_fields = ['created_at']


class ServiceSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)

    class Meta:
        model = Service
        fields = '__all__'
        read_only_fields = ['barber', 'created_at', 'updated_at']


class ServiceCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Service
        exclude = ['barber', 'created_at', 'updated_at']
