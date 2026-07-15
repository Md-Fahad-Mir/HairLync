from rest_framework import serializers
from Apps.profiles.models import SalonEmployee
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
        # `salon` / `available_employees` are exposed read-only here so the
        # existing barber endpoints can never be used to reassign ownership.
        read_only_fields = [
            'barber', 'salon', 'available_employees', 'created_at', 'updated_at',
        ]


class ServiceCreateSerializer(serializers.ModelSerializer):
    """Barber service create/update. Ownership fields are never client-settable."""
    class Meta:
        model = Service
        # `salon` and `available_employees` are excluded so a barber cannot
        # attach their service to a salon they do not own.
        exclude = ['barber', 'salon', 'available_employees', 'created_at', 'updated_at']


# ==============================================================================
# SALON SERVICE SERIALIZERS
# ==============================================================================
class SalonServiceSerializer(serializers.ModelSerializer):
    """Read serializer for salon-owned services (owner-facing)."""
    category_name = serializers.SerializerMethodField()
    salon_name = serializers.SerializerMethodField()
    available_employees = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    available_employee_names = serializers.SerializerMethodField()

    class Meta:
        model = Service
        fields = [
            'id', 'salon', 'salon_name', 'category', 'category_name', 'name',
            'description', 'price', 'duration_minutes', 'gender_target',
            'is_active', 'available_employees', 'available_employee_names',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'salon', 'created_at', 'updated_at']

    def get_category_name(self, obj):
        return obj.category.name if obj.category_id else None

    def get_salon_name(self, obj):
        return obj.salon.business_name if obj.salon_id else None

    def get_available_employee_names(self, obj):
        return [e.user.full_name for e in obj.available_employees.all()]


class SalonServicePublicSerializer(serializers.ModelSerializer):
    """Public serializer for clients browsing a salon's services."""
    category_name = serializers.SerializerMethodField()
    available_employees = serializers.PrimaryKeyRelatedField(many=True, read_only=True)

    class Meta:
        model = Service
        fields = [
            'id', 'salon', 'category', 'category_name', 'name', 'description',
            'price', 'duration_minutes', 'gender_target', 'available_employees',
        ]

    def get_category_name(self, obj):
        return obj.category.name if obj.category_id else None


class SalonServiceCreateUpdateSerializer(serializers.ModelSerializer):
    """
    Create/update a salon-owned service.

    The salon is taken from the authenticated owner and is never accepted from
    the request body. `available_employees` is validated to belong to that salon.
    """
    available_employees = serializers.PrimaryKeyRelatedField(
        many=True,
        required=False,
        queryset=SalonEmployee.objects.all(),
    )

    class Meta:
        model = Service
        fields = [
            'category', 'name', 'description', 'price', 'duration_minutes',
            'gender_target', 'is_active', 'available_employees',
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        salon = self.context.get('salon')
        if salon is not None:
            # Tenant-scope the queryset so an owner can only ever reference
            # employees of their own salon (blocks cross-salon FK attachment).
            self.fields['available_employees'].child_relation.queryset = (
                SalonEmployee.objects.filter(salon=salon)
            )

    def validate_price(self, value):
        if value is not None and value < 0:
            raise serializers.ValidationError("Price cannot be negative.")
        return value

    def validate_duration_minutes(self, value):
        if value is not None and value <= 0:
            raise serializers.ValidationError("Duration must be greater than zero.")
        return value

    def validate_available_employees(self, value):
        salon = self.context.get('salon')
        if salon is None:
            return value
        for employee in value:
            if employee.salon_id != salon.id:
                raise serializers.ValidationError(
                    "One or more employees do not belong to your salon."
                )
        return value

    def validate_name(self, value):
        salon = self.context.get('salon')
        value = value.strip()
        if salon is None:
            return value
        qs = Service.objects.filter(salon=salon, name=value)
        if self.instance is not None:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError(
                "Your salon already has a service with this name."
            )
        return value
