from django.db import models
from django.conf import settings


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
    """Individual service offered by a barber."""

    class Meta:
        verbose_name = 'Service'
        verbose_name_plural = 'Services'
        ordering = ['category', 'name']
        unique_together = ('barber', 'name')

    GENDER_CHOICES = [
        ('male', 'Male'),
        ('female', 'Female'),
        ('unisex', 'Unisex'),
    ]

    barber = models.ForeignKey(
        'profiles.BarberProfile',
        on_delete=models.CASCADE,
        related_name='services',
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
        return f"{self.name} - {self.barber.business_name}"
