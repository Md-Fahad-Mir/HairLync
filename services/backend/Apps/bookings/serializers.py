from rest_framework import serializers
from .models import Booking, TimeSlot


class BookingSerializer(serializers.ModelSerializer):
    client_name = serializers.CharField(source='client.full_name', read_only=True)
    client_email = serializers.CharField(source='client.email', read_only=True)
    barber_name = serializers.CharField(source='barber.business_name', read_only=True)
    service_name = serializers.CharField(source='service.name', read_only=True)
    can_cancel = serializers.SerializerMethodField()

    class Meta:
        model = Booking
        fields = '__all__'
        read_only_fields = [
            'client', 'status', 'barber_notes', 'cancellation_reason',
            'rejection_reason', 'rescheduled_from', 'created_at', 'updated_at',
        ]

    def get_can_cancel(self, obj):
        return obj.can_cancel()


class BookingCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Booking
        fields = ['barber', 'employee', 'service', 'date', 'start_time', 'end_time', 'notes']

    def validate(self, attrs):
        if attrs['start_time'] >= attrs['end_time']:
            raise serializers.ValidationError({"end_time": "End time must be after start time."})

        # Check for conflicts
        barber = attrs['barber']
        date = attrs['date']
        start = attrs['start_time']
        end = attrs['end_time']

        conflicts = Booking.objects.filter(
            barber=barber,
            date=date,
            status__in=['pending', 'approved'],
            start_time__lt=end,
            end_time__gt=start,
        )
        if attrs.get('employee'):
            conflicts = conflicts.filter(employee=attrs['employee'])

        if conflicts.exists():
            raise serializers.ValidationError("This time slot conflicts with an existing booking.")

        return attrs


class BookingStatusUpdateSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=['approved', 'rejected', 'completed', 'cancelled'])
    reason = serializers.CharField(required=False, default='')


class BookingRescheduleSerializer(serializers.Serializer):
    new_date = serializers.DateField()
    new_start_time = serializers.TimeField()
    new_end_time = serializers.TimeField()

    def validate(self, attrs):
        if attrs['new_start_time'] >= attrs['new_end_time']:
            raise serializers.ValidationError({"new_end_time": "End time must be after start time."})
        return attrs


class TimeSlotSerializer(serializers.ModelSerializer):
    class Meta:
        model = TimeSlot
        fields = '__all__'
        read_only_fields = ['barber', 'created_at']


class TimeSlotCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = TimeSlot
        fields = ['employee', 'date', 'start_time', 'end_time', 'is_available', 'is_blocked']
