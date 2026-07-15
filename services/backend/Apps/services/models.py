from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError


# ------------------------------------------------------------------------------
# SERVICE CATEGORY
# ------------------------------------------------------------------------------
class ServiceCategory(models.Model):
    """Category grouping for services."""

    class Meta:
        verbose_name = 'Service Category'
        verbose_name_plural = 'Service Categories'
        ordering = ['name']

    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, default='')
    icon = models.CharField(max_length=50, blank=True, default='', help_text='Icon name or CSS class')

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


# ------------------------------------------------------------------------------
# SERVICE
# ------------------------------------------------------------------------------
class Service(models.Model):
    """
    Individual service offered by a business, owned by exactly ONE of:

    Barber service (legacy):
        barber = BarberProfile, salon = None

    Salon service:
        barber = None, salon = SalonProfile

    Employee eligibility rule for salon services:
        - If `available_employees` is empty, EVERY active employee of the salon
          may provide the service.
        - If `available_employees` has entries, ONLY those employees may.
    """

    class Meta:
        verbose_name = 'Service'
        verbose_name_plural = 'Services'
        ordering = ['category', 'name']
        # Retained for barber services. Salon services have barber=NULL, which
        # SQL treats as distinct, so they are covered by the constraint below.
        unique_together = ('barber', 'name')
        constraints = [
            models.CheckConstraint(
                condition=(
                    models.Q(barber__isnull=False, salon__isnull=True)
                    | models.Q(barber__isnull=True, salon__isnull=False)
                ),
                name='service_exactly_one_owner',
            ),
            models.UniqueConstraint(
                fields=['salon', 'name'],
                condition=models.Q(salon__isnull=False),
                name='uniq_salon_service_name',
            ),
        ]

    GENDER_CHOICES = [
        ('male', 'Male'),
        ('female', 'Female'),
        ('unisex', 'Unisex'),
    ]

    barber = models.ForeignKey(
        'profiles.BarberProfile',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='services',
        help_text='Set for barber services. Null for salon services.',
    )
    salon = models.ForeignKey(
        'profiles.SalonProfile',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='services',
        help_text='Set for salon services. Null for barber services.',
    )
    available_employees = models.ManyToManyField(
        'profiles.SalonEmployee',
        blank=True,
        related_name='available_services',
        help_text='Salon services only. Empty means every active salon employee may provide it.',
    )
    category = models.ForeignKey(
        ServiceCategory,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='services',
    )
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True, default='')
    price = models.DecimalField(max_digits=10, decimal_places=2)
    duration_minutes = models.PositiveIntegerField(
        default=30,
        help_text='Duration in minutes'
    )
    gender_target = models.CharField(max_length=10, choices=GENDER_CHOICES, default='unisex')
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} - {self.owner_name or 'Unknown'}"

    @property
    def owner_name(self):
        """Display name of the owning business, whichever shape this service is."""
        if self.salon_id:
            return self.salon.business_name
        if self.barber_id:
            return self.barber.business_name
        return None

    @property
    def owner_type(self):
        return 'salon' if self.salon_id else 'barber'

    def clean(self):
        if not self.barber_id and not self.salon_id:
            raise ValidationError({'barber': 'A service must belong to either a barber or a salon.'})
        if self.barber_id and self.salon_id:
            raise ValidationError({'salon': 'A service cannot belong to both a barber and a salon.'})
