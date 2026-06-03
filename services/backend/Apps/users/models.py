from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils import timezone
from django.db import models
import random
import string
from django.conf import settings


# ------------------------------------------------------------------------------
# CUSTOM USER MANAGER
# ------------------------------------------------------------------------------
class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("The Email field must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)

        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()

        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)
        extra_fields.setdefault("role", "admin")

        if not password:
            raise ValueError("Superuser must have a password.")
        return self.create_user(email, password, **extra_fields)


# ------------------------------------------------------------------------------
# CUSTOM USER MODEL
# ------------------------------------------------------------------------------
class CustomUserModel(AbstractBaseUser, PermissionsMixin):
    class Meta:
        app_label = 'users'
        swappable = 'AUTH_USER_MODEL'
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        ordering = ['-date_joined']

    ROLE_CHOICES = [
        ('client', 'Client'),
        ('barber', 'Barber/Hair Stylist'),
        ('salon', 'Hair Salon'),
        ('admin', 'Admin'),
    ]

    CURRENT_PLAN_CHOICES = [
        ('free', 'Free'),
        ('monthly', 'Monthly'),
        ('yearly', 'Yearly'),
    ]

    # Core fields
    email = models.EmailField(unique=True, db_index=True)
    full_name = models.CharField(max_length=255, blank=True, default='')
    phone_number = models.CharField(max_length=20, blank=True, default='')
    country = models.CharField(max_length=100, blank=True, default='')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='client', db_index=True)

    # Sub-profile fields (for salon employees)
    is_sub_profile = models.BooleanField(
        default=False,
        help_text='True if this user is a salon employee sub-profile account.'
    )
    parent_salon = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='sub_profiles',
        limit_choices_to={'role': 'salon', 'is_sub_profile': False},
        help_text='The salon owner who created this sub-profile.',
    )

    # Status fields
    is_active = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(auto_now=True)

    # Subscription fields
    paid_user = models.BooleanField(default=False)
    current_plan = models.CharField(max_length=20, choices=CURRENT_PLAN_CHOICES, default='free')
    current_period_start = models.DateTimeField(blank=True, null=True)
    current_period_end = models.DateTimeField(blank=True, null=True)

    objects = CustomUserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email

    @property
    def is_client(self):
        return self.role == 'client'

    @property
    def is_barber(self):
        return self.role == 'barber'

    @property
    def is_salon(self):
        return self.role == 'salon'

    @property
    def is_salon_owner(self):
        """True if this is a salon account that is NOT a sub-profile."""
        return self.role == 'salon' and not self.is_sub_profile

    @property
    def is_salon_employee(self):
        """True if this is a salon sub-profile (employee)."""
        return self.role == 'salon' and self.is_sub_profile

    @property
    def is_admin_user(self):
        return self.role == 'admin'

    def is_subscribed(self):
        """Check if user has an active paid subscription."""
        if not self.paid_user or self.current_plan == 'free':
            return False
        if self.current_period_end and self.current_period_end < timezone.now():
            return False
        return True

    def get_subscription_period(self):
        """Returns subscription period in human-readable format."""
        if self.current_period_start and self.current_period_end:
            return f"{self.current_period_start} - {self.current_period_end}"
        return "No active subscription"


# ------------------------------------------------------------------------------
# PENDING USER
# ------------------------------------------------------------------------------
class PendingUser(models.Model):
    class Meta:
        app_label = 'users'
        verbose_name = 'Pending User'
        verbose_name_plural = 'Pending Users'

    email = models.EmailField(unique=True)
    full_name = models.CharField(max_length=255, blank=True, default='')
    password = models.CharField(max_length=255)
    role = models.CharField(max_length=20, default='client')
    otp = models.CharField(max_length=6, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    otp_created_at = models.DateTimeField(null=True, blank=True)

    OTP_TTL_SECONDS = 15 * 60  # 15 minutes

    def __str__(self):
        return self.email

    def generate_otp(self):
        self.otp = f"{random.randint(0, 999999):06d}"
        self.otp_created_at = timezone.now()
        self.save(update_fields=["otp", "otp_created_at"])
        return self.otp

    def verify_otp(self, otp):
        if not self.otp or not self.otp_created_at:
            return False, "No OTP requested"
        if (timezone.now() - self.otp_created_at).total_seconds() > self.OTP_TTL_SECONDS:
            return False, "OTP expired"
        if str(self.otp) != str(otp):
            return False, "Invalid OTP"
        return True, None


# ------------------------------------------------------------------------------
# FORGOT PASSWORD OTP
# ------------------------------------------------------------------------------
class ForgotPasswordRequest(models.Model):
    class Meta:
        app_label = 'users'
        verbose_name = 'Forgot Password Request'
        verbose_name_plural = 'Forgot Password Requests'

    email = models.EmailField(unique=True)
    otp = models.CharField(max_length=6, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    otp_created_at = models.DateTimeField(null=True, blank=True)

    OTP_TTL_SECONDS = 15 * 60  # 15 minutes

    def __str__(self):
        return self.email

    def generate_otp(self):
        self.otp = f"{random.randint(0, 999999):06d}"
        self.otp_created_at = timezone.now()
        self.save(update_fields=["otp", "otp_created_at"])
        return self.otp

    def verify_otp(self, otp):
        if not self.otp or not self.otp_created_at:
            return False, "No OTP requested"
        if (timezone.now() - self.otp_created_at).total_seconds() > self.OTP_TTL_SECONDS:
            return False, "OTP expired"
        if str(self.otp) != str(otp):
            return False, "Invalid OTP"
        return True, None
