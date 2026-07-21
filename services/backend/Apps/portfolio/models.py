from django.db import models
from django.conf import settings


class PortfolioItem(models.Model):
    """Portfolio image/work showcased by a barber, salon, or salon employee."""

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

    OWNER_TYPE_CHOICES = [
        ('barber', 'Barber'),
        ('salon', 'Salon'),
        ('salon_employee', 'Salon Employee'),
    ]

    # Support multiple owner types: barber, salon, or salon_employee
    owner_type = models.CharField(max_length=20, choices=OWNER_TYPE_CHOICES, default='barber')

    barber = models.ForeignKey(
        'profiles.BarberProfile',
        on_delete=models.CASCADE,
        related_name='portfolio_items',
        null=True,
        blank=True,
    )
    salon = models.ForeignKey(
        'profiles.SalonProfile',
        on_delete=models.CASCADE,
        related_name='portfolio_items',
        null=True,
        blank=True,
    )
    salon_employee = models.ForeignKey(
        'profiles.SalonEmployee',
        on_delete=models.CASCADE,
        related_name='portfolio_items',
        null=True,
        blank=True,
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

    def get_owner_name(self):
        """Return the name of the portfolio item's owner."""
        if self.owner_type == 'barber' and self.barber:
            return self.barber.business_name
        elif self.owner_type == 'salon' and self.salon:
            return self.salon.business_name
        elif self.owner_type == 'salon_employee' and self.salon_employee:
            return self.salon_employee.full_name
        return 'Unknown'

    def __str__(self):
        return f"{self.title} by {self.get_owner_name()}"
