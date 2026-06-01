from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator


# ------------------------------------------------------------------------------
# CLIENT PROFILE
# ------------------------------------------------------------------------------
class ClientProfile(models.Model):
    """Profile for client (customer) users."""

    class Meta:
        verbose_name = 'Client Profile'
        verbose_name_plural = 'Client Profiles'

    HAIR_TYPE_CHOICES = [
        ('straight', 'Straight'),
        ('wavy', 'Wavy'),
        ('curly', 'Curly'),
        ('coily', 'Coily'),
    ]

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='client_profile',
        limit_choices_to={'role': 'client'},
    )
    avatar = models.ImageField(upload_to='profiles/clients/avatars/', blank=True, null=True)
    bio = models.TextField(blank=True, default='')
    date_of_birth = models.DateField(blank=True, null=True)
    gender = models.CharField(max_length=20, blank=True, default='')
    city = models.CharField(max_length=100, blank=True, default='')
    address = models.TextField(blank=True, default='')
    hair_type = models.CharField(max_length=20, choices=HAIR_TYPE_CHOICES, blank=True, default='')
    preferred_hair_length = models.CharField(max_length=20, blank=True, default='')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Client: {self.user.email}"


# ------------------------------------------------------------------------------
# BARBER PROFILE
# ------------------------------------------------------------------------------
class BarberProfile(models.Model):
    """Business profile for barber/hairdresser users."""

    class Meta:
        verbose_name = 'Barber Profile'
        verbose_name_plural = 'Barber Profiles'
        indexes = [
            models.Index(fields=['city', 'is_verified']),
            models.Index(fields=['average_rating']),
        ]

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='barber_profile',
        limit_choices_to={'role': 'barber'},
    )
    business_name = models.CharField(max_length=255)
    avatar = models.ImageField(upload_to='profiles/barbers/avatars/', blank=True, null=True)
    cover_image = models.ImageField(upload_to='profiles/barbers/covers/', blank=True, null=True)
    bio = models.TextField(blank=True, default='')
    experience_years = models.PositiveIntegerField(default=0)

    # Location
    city = models.CharField(max_length=100, blank=True, default='', db_index=True)
    address = models.TextField(blank=True, default='')
    latitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)

    # Categories
    CATEGORY_CHOICES = [
        ('barber', 'Barber'),
        ('hairdresser', 'Hairdresser'),
        ('stylist', 'Stylist'),
        ('colorist', 'Colorist'),
        ('braider', 'Braider'),
        ('unisex', 'Unisex Salon'),
    ]
    category = models.CharField(max_length=30, choices=CATEGORY_CHOICES, default='barber', db_index=True)

    # Verification & Status
    is_verified = models.BooleanField(default=False)
    verification_badge = models.CharField(max_length=50, blank=True, default='')
    is_accepting_clients = models.BooleanField(default=True)

    # Ratings (denormalized for performance)
    average_rating = models.DecimalField(
        max_digits=3, decimal_places=2, default=0.00,
        validators=[MinValueValidator(0), MaxValueValidator(5)]
    )
    total_reviews = models.PositiveIntegerField(default=0)
    total_bookings = models.PositiveIntegerField(default=0)

    # Working hours (JSON stored as text for flexibility)
    working_hours = models.JSONField(
        default=dict,
        blank=True,
        help_text='Working hours by day: {"monday": {"open": "09:00", "close": "18:00"}, ...}'
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Barber: {self.business_name} ({self.user.email})"


# ------------------------------------------------------------------------------
# EMPLOYEE / SUB-PROFILE
# ------------------------------------------------------------------------------
class EmployeeProfile(models.Model):
    """Employee sub-profile under a barber business."""

    class Meta:
        verbose_name = 'Employee Profile'
        verbose_name_plural = 'Employee Profiles'
        unique_together = ('barber', 'user')

    barber = models.ForeignKey(
        BarberProfile,
        on_delete=models.CASCADE,
        related_name='employees',
    )
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='employee_profile',
    )
    position = models.CharField(max_length=100, blank=True, default='Stylist')
    avatar = models.ImageField(upload_to='profiles/employees/avatars/', blank=True, null=True)
    bio = models.TextField(blank=True, default='')
    specialties = models.TextField(blank=True, default='', help_text='Comma-separated list of specialties')
    is_active = models.BooleanField(default=True)

    # Permissions
    can_manage_bookings = models.BooleanField(default=True)
    can_manage_schedule = models.BooleanField(default=True)
    can_access_tools = models.BooleanField(default=True)
    can_manage_employees = models.BooleanField(default=False)
    can_delete_business = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Employee: {self.user.email} at {self.barber.business_name}"
