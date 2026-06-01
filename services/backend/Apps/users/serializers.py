from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

User = get_user_model()


# ------------------------------------------------------------------------------
# AUTH SERIALIZERS
# ------------------------------------------------------------------------------
class RegisterSerializer(serializers.Serializer):
    """Serializer for user registration - creates a PendingUser with OTP."""
    email = serializers.EmailField()
    full_name = serializers.CharField(max_length=255)
    password = serializers.CharField(write_only=True, min_length=8)
    confirm_password = serializers.CharField(write_only=True, min_length=8)
    role = serializers.ChoiceField(choices=['client', 'barber'], default='client')

    def validate_email(self, value):
        email = value.lower().strip()
        if User.objects.filter(email=email).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return email

    def validate(self, attrs):
        if attrs['password'] != attrs['confirm_password']:
            raise serializers.ValidationError({"confirm_password": "Passwords do not match."})
        validate_password(attrs['password'])
        return attrs


class VerifyOTPSerializer(serializers.Serializer):
    """Serializer for OTP verification during registration."""
    email = serializers.EmailField()
    otp = serializers.CharField(max_length=6, min_length=6)


class ResendOTPSerializer(serializers.Serializer):
    """Serializer for resending OTP."""
    email = serializers.EmailField()


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """Custom JWT token serializer that includes user role and details."""

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['email'] = user.email
        token['role'] = user.role
        token['full_name'] = user.full_name
        token['is_verified'] = user.is_verified
        return token

    def validate(self, attrs):
        data = super().validate(attrs)
        data['user'] = {
            'id': self.user.id,
            'email': self.user.email,
            'full_name': self.user.full_name,
            'role': self.user.role,
            'is_verified': self.user.is_verified,
            'is_subscribed': self.user.is_subscribed(),
        }
        return data


class ForgotPasswordSerializer(serializers.Serializer):
    """Serializer for forgot password request."""
    email = serializers.EmailField()


class ResetPasswordSerializer(serializers.Serializer):
    """Serializer for password reset with OTP."""
    email = serializers.EmailField()
    otp = serializers.CharField(max_length=6, min_length=6)
    new_password = serializers.CharField(write_only=True, min_length=8)
    confirm_password = serializers.CharField(write_only=True, min_length=8)

    def validate(self, attrs):
        if attrs['new_password'] != attrs['confirm_password']:
            raise serializers.ValidationError({"confirm_password": "Passwords do not match."})
        validate_password(attrs['new_password'])
        return attrs


class ChangePasswordSerializer(serializers.Serializer):
    """Serializer for changing password (authenticated)."""
    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True, min_length=8)
    confirm_password = serializers.CharField(write_only=True, min_length=8)

    def validate(self, attrs):
        if attrs['new_password'] != attrs['confirm_password']:
            raise serializers.ValidationError({"confirm_password": "Passwords do not match."})
        validate_password(attrs['new_password'])
        return attrs


# ------------------------------------------------------------------------------
# USER SERIALIZERS
# ------------------------------------------------------------------------------
class UserSerializer(serializers.ModelSerializer):
    """Full user serializer for user details."""
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            'id', 'email', 'full_name', 'phone_number', 'country',
            'role', 'is_active', 'is_verified', 'date_joined',
            'paid_user', 'current_plan', 'is_subscribed',
        ]
        read_only_fields = [
            'id', 'email', 'role', 'is_active', 'is_verified',
            'date_joined', 'paid_user', 'current_plan',
        ]

    def get_is_subscribed(self, obj):
        return obj.is_subscribed()


class UserUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating user profile fields."""

    class Meta:
        model = User
        fields = ['full_name', 'phone_number', 'country']


class UserListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for listing users (admin)."""

    class Meta:
        model = User
        fields = ['id', 'email', 'full_name', 'role', 'is_active', 'is_verified', 'date_joined']
        read_only_fields = fields
