from rest_framework import serializers
from .models import ClientProfile, BarberProfile, SalonProfile, SalonEmployee
from Apps.users.serializers import UserSerializer


# ==============================================================================
# CLIENT PROFILE SERIALIZERS
# ==============================================================================
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


# ==============================================================================
# BARBER / HAIR STYLIST PROFILE SERIALIZERS
# ==============================================================================
class BarberProfileSerializer(serializers.ModelSerializer):
    """Full read serializer for barber profile."""
    user = UserSerializer(read_only=True)
    services_count = serializers.SerializerMethodField()
    portfolio_count = serializers.SerializerMethodField()
    gallery_images = serializers.SerializerMethodField()

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

    def get_gallery_images(self, obj):
        return obj.gallery_images


class BarberProfileUpdateSerializer(serializers.ModelSerializer):
    """Serializer for creating/updating barber profile."""
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
            'is_accepting_clients', 'experience_years', 'specialties',
        ]


# ==============================================================================
# HAIR SALON PROFILE SERIALIZERS
# ==============================================================================
class SalonProfileSerializer(serializers.ModelSerializer):
    """Full read serializer for salon profile."""
    user = UserSerializer(read_only=True)
    employees_count = serializers.SerializerMethodField()
    services_count = serializers.SerializerMethodField()
    portfolio_count = serializers.SerializerMethodField()
    gallery_images = serializers.SerializerMethodField()

    class Meta:
        model = SalonProfile
        fields = '__all__'
        read_only_fields = [
            'user', 'average_rating', 'total_reviews', 'total_bookings',
            'is_verified', 'verification_badge', 'created_at', 'updated_at',
        ]

    def get_employees_count(self, obj):
        return obj.employees.filter(is_active=True).count()

    def get_services_count(self, obj):
        # Services will be linked to the salon via the barber FK
        # For now return 0 until service model is updated
        if hasattr(obj, 'services'):
            return obj.services.filter(is_active=True).count()
        return 0

    def get_portfolio_count(self, obj):
        if hasattr(obj, 'portfolio_items'):
            return obj.portfolio_items.count()
        return 0

    def get_gallery_images(self, obj):
        return obj.gallery_images


class SalonProfileUpdateSerializer(serializers.ModelSerializer):
    """Serializer for creating/updating salon profile."""
    class Meta:
        model = SalonProfile
        exclude = [
            'user', 'average_rating', 'total_reviews', 'total_bookings',
            'is_verified', 'verification_badge', 'created_at', 'updated_at',
        ]


class SalonProfileListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for salon listing/search."""
    user_name = serializers.CharField(source='user.full_name', read_only=True)
    employees_count = serializers.SerializerMethodField()

    class Meta:
        model = SalonProfile
        fields = [
            'id', 'user', 'user_name', 'business_name', 'avatar',
            'city', 'is_verified', 'average_rating', 'total_reviews',
            'is_accepting_clients', 'experience_years', 'employees_count',
        ]

    def get_employees_count(self, obj):
        return obj.employees.filter(is_active=True).count()


# ==============================================================================
# SALON EMPLOYEE (SUB-PROFILE) SERIALIZERS
# ==============================================================================
class SalonEmployeeSerializer(serializers.ModelSerializer):
    """Read serializer for salon employees - includes generated credentials."""
    user = UserSerializer(read_only=True)

    class Meta:
        model = SalonEmployee
        fields = '__all__'
        read_only_fields = [
            'salon', 'user', 'generated_email', 'generated_password',
            'average_rating', 'total_reviews', 'total_bookings',
            'created_at', 'updated_at',
        ]


class SalonEmployeePublicSerializer(serializers.ModelSerializer):
    """
    Public serializer for salon employees - used in salon profile display.
    Does NOT expose generated credentials.
    """
    user_name = serializers.CharField(source='user.full_name', read_only=True)

    class Meta:
        model = SalonEmployee
        fields = [
            'id', 'user_name', 'position', 'role_title', 'avatar',
            'specialties', 'experience_years', 'experience_range',
            'average_rating', 'total_reviews', 'total_bookings',
            'is_active',
        ]


class SalonEmployeeCreateSerializer(serializers.Serializer):
    """
    Serializer for creating a salon employee sub-profile.
    Only requires the employee's full name - email and password are auto-generated.
    """
    full_name = serializers.CharField(max_length=255)
    position = serializers.CharField(max_length=100, required=False, default='Hair Stylist')
    role_title = serializers.CharField(max_length=100, required=False, default='Hair Stylist')

    def validate_full_name(self, value):
        value = value.strip()
        if not value:
            raise serializers.ValidationError("Full name is required.")
        if len(value.split()) < 2:
            raise serializers.ValidationError(
                "Please provide both first name and last name."
            )
        return value


class SalonEmployeeUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating employee profile fields (by the employee themselves)."""
    class Meta:
        model = SalonEmployee
        fields = [
            'position', 'role_title', 'avatar', 'cover_image', 'bio',
            'specialties', 'experience_years', 'experience_range',
        ]
