from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
import random
import string


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
# BARBER / HAIR STYLIST PROFILE
# ------------------------------------------------------------------------------
class BarberProfile(models.Model):
    """Business profile for barber/hair stylist users."""

    class Meta:
        verbose_name = 'Barber Profile'
        verbose_name_plural = 'Barber Profiles'
        indexes = [
            models.Index(fields=['city', 'is_verified']),
            models.Index(fields=['average_rating']),
        ]

    EXPERIENCE_CHOICES = [
        ('1-3', '1-3 Years'),
        ('3-5', '3-5 Years'),
        ('5-10', '5-10 Years'),
        ('10+', '10+ Years'),
    ]

    CATEGORY_CHOICES = [
        ('barber', 'Barber'),
        ('hairdresser', 'Hairdresser'),
        ('stylist', 'Stylist'),
        ('colorist', 'Colorist'),
        ('braider', 'Braider'),
        ('unisex', 'Unisex Salon'),
    ]

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='barber_profile',
        limit_choices_to={'role': 'barber'},
    )

    # Basic info (from "Create Your Profile" screen)
    business_name = models.CharField(max_length=255)
    role_title = models.CharField(
        max_length=100, blank=True, default='Barber',
        help_text='Professional role: Barber, Hair Stylist, etc.',
    )
    avatar = models.ImageField(upload_to='profiles/barbers/avatars/', blank=True, null=True)
    cover_image = models.ImageField(upload_to='profiles/barbers/covers/', blank=True, null=True)
    bio = models.TextField(blank=True, default='', help_text='About you / what makes you unique')

    # Experience (from "What You Offer" screen)
    experience_years = models.PositiveIntegerField(default=0)
    experience_range = models.CharField(
        max_length=10, choices=EXPERIENCE_CHOICES, blank=True, default='',
        help_text='Experience range selection from profile setup',
    )

    # Location (from "Locations & Hours" screen)
    city = models.CharField(max_length=100, blank=True, default='', db_index=True)
    address = models.TextField(blank=True, default='')
    latitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)

    # Contact (from "Contact & Gallery" screen)
    phone_number = models.CharField(max_length=20, blank=True, default='')

    # Categories
    category = models.CharField(max_length=30, choices=CATEGORY_CHOICES, default='barber', db_index=True)

    # Specialties (badges like "Fades", "Braids", "Perms" from profile display)
    specialties = models.JSONField(
        default=list, blank=True,
        help_text='List of specialty tags, e.g. ["Fades", "Braids", "Perms"]',
    )

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

    # Working hours (JSON stored for flexibility)
    working_days = models.JSONField(
        default=list, blank=True,
        help_text='List of working days, e.g. ["M", "T", "W", "T", "F", "S", "S"]',
    )
    working_hours = models.JSONField(
        default=dict, blank=True,
        help_text='Working hours: {"opening_time": "09:00", "opening_period": "AM", "closing_time": "06:00", "closing_period": "PM"}',
    )

    # Gallery images (from "Contact & Gallery" screen, up to 6 images)
    gallery_image_1 = models.ImageField(upload_to='profiles/barbers/gallery/', blank=True, null=True)
    gallery_image_2 = models.ImageField(upload_to='profiles/barbers/gallery/', blank=True, null=True)
    gallery_image_3 = models.ImageField(upload_to='profiles/barbers/gallery/', blank=True, null=True)
    gallery_image_4 = models.ImageField(upload_to='profiles/barbers/gallery/', blank=True, null=True)
    gallery_image_5 = models.ImageField(upload_to='profiles/barbers/gallery/', blank=True, null=True)
    gallery_image_6 = models.ImageField(upload_to='profiles/barbers/gallery/', blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Barber: {self.business_name} ({self.user.email})"

    @property
    def gallery_images(self):
        """Return a list of non-null gallery image URLs."""
        images = []
        for i in range(1, 7):
            img = getattr(self, f'gallery_image_{i}')
            if img:
                images.append(img.url)
        return images


# ------------------------------------------------------------------------------
# HAIR SALON PROFILE
# ------------------------------------------------------------------------------
class SalonProfile(models.Model):
    """Business profile for Hair Salon users."""

    class Meta:
        verbose_name = 'Salon Profile'
        verbose_name_plural = 'Salon Profiles'
        indexes = [
            models.Index(fields=['city', 'is_verified']),
            models.Index(fields=['average_rating']),
        ]

    EXPERIENCE_CHOICES = [
        ('1-3', '1-3 Years'),
        ('3-5', '3-5 Years'),
        ('5-10', '5-10 Years'),
        ('10+', '10+ Years'),
    ]

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='salon_profile',
        limit_choices_to={'role': 'salon', 'is_sub_profile': False},
    )

    # Basic info
    business_name = models.CharField(max_length=255)
    avatar = models.ImageField(upload_to='profiles/salons/avatars/', blank=True, null=True)
    cover_image = models.ImageField(upload_to='profiles/salons/covers/', blank=True, null=True)
    bio = models.TextField(blank=True, default='')

    # Experience
    experience_years = models.PositiveIntegerField(default=0)
    experience_range = models.CharField(
        max_length=10, choices=EXPERIENCE_CHOICES, blank=True, default='',
    )

    # Location
    city = models.CharField(max_length=100, blank=True, default='', db_index=True)
    address = models.TextField(blank=True, default='')
    latitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)

    # Contact
    phone_number = models.CharField(max_length=20, blank=True, default='')

    # Verification & Status
    is_verified = models.BooleanField(default=False)
    verification_badge = models.CharField(max_length=50, blank=True, default='')
    is_accepting_clients = models.BooleanField(default=True)

    # Ratings (denormalized)
    average_rating = models.DecimalField(
        max_digits=3, decimal_places=2, default=0.00,
        validators=[MinValueValidator(0), MaxValueValidator(5)]
    )
    total_reviews = models.PositiveIntegerField(default=0)
    total_bookings = models.PositiveIntegerField(default=0)

    # Working hours
    working_days = models.JSONField(
        default=list, blank=True,
        help_text='List of working days, e.g. ["M", "T", "W", "T", "F", "S", "S"]',
    )
    working_hours = models.JSONField(
        default=dict, blank=True,
        help_text='Working hours: {"opening_time": "09:00", "opening_period": "AM", "closing_time": "06:00", "closing_period": "PM"}',
    )

    # Gallery images (up to 6)
    gallery_image_1 = models.ImageField(upload_to='profiles/salons/gallery/', blank=True, null=True)
    gallery_image_2 = models.ImageField(upload_to='profiles/salons/gallery/', blank=True, null=True)
    gallery_image_3 = models.ImageField(upload_to='profiles/salons/gallery/', blank=True, null=True)
    gallery_image_4 = models.ImageField(upload_to='profiles/salons/gallery/', blank=True, null=True)
    gallery_image_5 = models.ImageField(upload_to='profiles/salons/gallery/', blank=True, null=True)
    gallery_image_6 = models.ImageField(upload_to='profiles/salons/gallery/', blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Salon: {self.business_name} ({self.user.email})"

    @property
    def gallery_images(self):
        """Return a list of non-null gallery image URLs."""
        images = []
        for i in range(1, 7):
            img = getattr(self, f'gallery_image_{i}')
            if img:
                images.append(img.url)
        return images


# ------------------------------------------------------------------------------
# SALON EMPLOYEE / SUB-PROFILE
# ------------------------------------------------------------------------------
class SalonEmployee(models.Model):
    """
    Employee sub-profile under a Hair Salon business.

    When a salon creates an employee, the system auto-generates login
    credentials (email + password). The employee can then log in and
    complete their own profile setup.

    Restrictions for sub-profile users:
    - Cannot delete their own account
    - Cannot delete any other account
    - Cannot create additional sub-profiles
    - Cannot manage, edit, or access other employee profiles
    - Cannot manage the main Hair Salon account
    """

    class Meta:
        verbose_name = 'Salon Employee'
        verbose_name_plural = 'Salon Employees'
        unique_together = ('salon', 'user')

    EXPERIENCE_CHOICES = [
        ('1-3', '1-3 Years'),
        ('3-5', '3-5 Years'),
        ('5-10', '5-10 Years'),
        ('10+', '10+ Years'),
    ]

    salon = models.ForeignKey(
        SalonProfile,
        on_delete=models.CASCADE,
        related_name='employees',
    )
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='employee_profile',
    )

    # Auto-generated credentials (stored for salon owner to view)
    generated_email = models.EmailField(
        unique=True,
        help_text='Auto-generated login email (firstname+lastname+2digits@hairlync.app)',
    )
    generated_password = models.CharField(
        max_length=8,
        help_text='Auto-generated 8-character password (stored for display to salon owner)',
    )

    # Employee profile fields
    position = models.CharField(max_length=100, blank=True, default='Hair Stylist')
    role_title = models.CharField(max_length=100, blank=True, default='Hair Stylist')
    avatar = models.ImageField(upload_to='profiles/employees/avatars/', blank=True, null=True)
    cover_image = models.ImageField(upload_to='profiles/employees/covers/', blank=True, null=True)
    bio = models.TextField(blank=True, default='')
    specialties = models.JSONField(
        default=list, blank=True,
        help_text='List of specialty tags, e.g. ["Fades", "Braids", "Perms"]',
    )
    experience_years = models.PositiveIntegerField(default=0)
    experience_range = models.CharField(
        max_length=10, choices=EXPERIENCE_CHOICES, blank=True, default='',
    )

    # Ratings (denormalized, per-employee)
    average_rating = models.DecimalField(
        max_digits=3, decimal_places=2, default=0.00,
        validators=[MinValueValidator(0), MaxValueValidator(5)]
    )
    total_reviews = models.PositiveIntegerField(default=0)
    total_bookings = models.PositiveIntegerField(default=0)

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Employee: {self.user.full_name} at {self.salon.business_name}"

    # ------------------------------------------------------------------
    # Credential generation utilities
    # ------------------------------------------------------------------
    @staticmethod
    def generate_employee_email(first_name, last_name):
        """
        Generate a unique login email for an employee sub-profile.
        Format: firstname + lastname + 2 random digits + @hairlync.app
        Example: johnsmith42@hairlync.app
        """
        from django.contrib.auth import get_user_model
        User = get_user_model()

        base = (first_name + last_name).lower().strip()
        # Remove any non-alphanumeric characters
        base = ''.join(c for c in base if c.isalnum())

        # Try up to 100 times to find a unique email
        for _ in range(100):
            digits = f"{random.randint(10, 99)}"
            email = f"{base}{digits}@hairlync.app"
            if not User.objects.filter(email=email).exists():
                return email

        # Fallback: use more digits
        digits = f"{random.randint(100, 9999)}"
        return f"{base}{digits}@hairlync.app"

    @staticmethod
    def generate_employee_password():
        """
        Generate an 8-character password with mix of digits, uppercase letters,
        and special characters.
        Example: 582A@17B
        """
        # Ensure at least: 2 uppercase, 1 special char, rest digits
        uppercase = random.choices(string.ascii_uppercase, k=2)
        special = random.choice(['@', '#', '$', '!', '&', '*'])
        digits = random.choices(string.digits, k=5)

        # Combine and shuffle
        password_chars = uppercase + [special] + digits
        random.shuffle(password_chars)
        return ''.join(password_chars)
