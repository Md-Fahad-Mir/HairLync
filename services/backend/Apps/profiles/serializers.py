from rest_framework import serializers
from .models import ClientProfile, BarberProfile, EmployeeProfile
from Apps.users.serializers import UserSerializer


class ClientProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = ClientProfile
        fields = '__all__'
        read_only_fields = ['user', 'created_at', 'updated_at']


class ClientProfileUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClientProfile
        exclude = ['user', 'created_at', 'updated_at']


class BarberProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    services_count = serializers.SerializerMethodField()
    portfolio_count = serializers.SerializerMethodField()
    employees_count = serializers.SerializerMethodField()

    class Meta:
        model = BarberProfile
        fields = '__all__'
        read_only_fields = [
            'user', 'average_rating', 'total_reviews', 'total_bookings',
            'is_verified', 'verification_badge', 'created_at', 'updated_at',
        ]

    def get_services_count(self, obj):
        return obj.services.filter(is_active=True).count()

    def get_portfolio_count(self, obj):
        return obj.portfolio_items.count()

    def get_employees_count(self, obj):
        return obj.employees.filter(is_active=True).count()


class BarberProfileUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = BarberProfile
        exclude = [
            'user', 'average_rating', 'total_reviews', 'total_bookings',
            'is_verified', 'verification_badge', 'created_at', 'updated_at',
        ]


class BarberProfileListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for barber listing/search."""
    user_name = serializers.CharField(source='user.full_name', read_only=True)

    class Meta:
        model = BarberProfile
        fields = [
            'id', 'user', 'user_name', 'business_name', 'avatar', 'category',
            'city', 'is_verified', 'average_rating', 'total_reviews',
            'is_accepting_clients', 'experience_years',
        ]


class EmployeeProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = EmployeeProfile
        fields = '__all__'
        read_only_fields = ['barber', 'user', 'created_at', 'updated_at']


class EmployeeCreateSerializer(serializers.Serializer):
    email = serializers.EmailField()
    full_name = serializers.CharField(max_length=255)
    password = serializers.CharField(write_only=True, min_length=8)
    position = serializers.CharField(max_length=100, required=False, default='Stylist')
    can_manage_bookings = serializers.BooleanField(required=False, default=True)
    can_manage_schedule = serializers.BooleanField(required=False, default=True)
    can_access_tools = serializers.BooleanField(required=False, default=True)
