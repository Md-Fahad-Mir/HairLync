from django.db import models
from django.conf import settings


class HairStyleCategory(models.Model):
    """Categories for hairstyle recommendations by occasion."""
    class Meta:
        verbose_name = 'Hair Style Category'
        verbose_name_plural = 'Hair Style Categories'
        ordering = ['name']

    OCCASION_CHOICES = [
        ('casual', 'Casual'),
        ('formal', 'Formal'),
        ('wedding', 'Wedding'),
        ('party', 'Party'),
        ('business', 'Business'),
        ('date', 'Date Night'),
        ('everyday', 'Everyday'),
    ]

    name = models.CharField(max_length=100)
    occasion = models.CharField(max_length=20, choices=OCCASION_CHOICES, default='everyday')
    description = models.TextField(blank=True, default='')
    image = models.ImageField(upload_to='recommendations/categories/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.occasion})"


class ClientImage(models.Model):
    """Images uploaded for AI recommendation processing."""
    class Meta:
        verbose_name = 'Client Image'
        verbose_name_plural = 'Client Images'
        ordering = ['-created_at']

    HAIR_LENGTH_CHOICES = [
        ('short', 'Short'),
        ('medium', 'Medium'),
        ('long', 'Long'),
    ]

    barber = models.ForeignKey(
        'profiles.BarberProfile',
        on_delete=models.CASCADE,
        related_name='client_images',
    )
    client = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='recommendation_images',
        null=True, blank=True,
    )
    image = models.ImageField(upload_to='recommendations/client_images/')
    hair_length = models.CharField(max_length=10, choices=HAIR_LENGTH_CHOICES, blank=True, default='')
    notes = models.TextField(blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Image for {self.client} by {self.barber}"


class StyleRecommendation(models.Model):
    """AI-generated or professional hairstyle/treatment recommendation."""
    class Meta:
        verbose_name = 'Style Recommendation'
        verbose_name_plural = 'Style Recommendations'
        ordering = ['-created_at']

    barber = models.ForeignKey(
        'profiles.BarberProfile',
        on_delete=models.CASCADE,
        related_name='recommendations',
    )
    client = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='received_recommendations',
    )
    client_image = models.ForeignKey(
        ClientImage,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='recommendations',
    )
    category = models.ForeignKey(
        HairStyleCategory,
        on_delete=models.SET_NULL,
        null=True, blank=True,
    )
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, default='')
    reference_image = models.ImageField(upload_to='recommendations/references/', blank=True, null=True)
    suggested_services = models.ManyToManyField('services.Service', blank=True, related_name='recommendations')
    suggested_products = models.TextField(blank=True, default='', help_text='Product recommendations as text')
    suggested_treatments = models.TextField(blank=True, default='', help_text='Treatment recommendations')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Recommendation: {self.title} for {self.client.email}"
