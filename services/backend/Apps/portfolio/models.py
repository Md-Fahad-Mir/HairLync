from django.db import models
from django.conf import settings


class PortfolioItem(models.Model):
    """Portfolio image/work showcased by a barber."""

    class Meta:
        verbose_name = 'Portfolio Item'
        verbose_name_plural = 'Portfolio Items'
        ordering = ['-created_at']

    CATEGORY_CHOICES = [
        ('haircut', 'Haircut'),
        ('coloring', 'Coloring'),
        ('styling', 'Styling'),
        ('treatment', 'Treatment'),
        ('braiding', 'Braiding'),
        ('beard', 'Beard'),
        ('other', 'Other'),
    ]

    barber = models.ForeignKey(
        'profiles.BarberProfile',
        on_delete=models.CASCADE,
        related_name='portfolio_items',
    )
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, default='')
    image = models.ImageField(upload_to='portfolio/images/')
    before_image = models.ImageField(upload_to='portfolio/before/', blank=True, null=True)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='haircut')
    tags = models.CharField(max_length=500, blank=True, default='', help_text='Comma-separated tags')
    is_featured = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title} by {self.barber.business_name}"
