from rest_framework import serializers
from .models import Favorite
from Apps.profiles.serializers import BarberProfileListSerializer


class FavoriteSerializer(serializers.ModelSerializer):
    barber_details = BarberProfileListSerializer(source='barber', read_only=True)

    class Meta:
        model = Favorite
        fields = '__all__'
        read_only_fields = ['client', 'created_at']


class FavoriteCreateSerializer(serializers.Serializer):
    barber_id = serializers.IntegerField()
