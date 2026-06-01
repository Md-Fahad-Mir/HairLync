from django.db import models
from django.conf import settings


# ------------------------------------------------------------------------------
# FAVORITE
# ------------------------------------------------------------------------------
class Favorite(models.Model):
    """Client's saved/favorite barbers."""

    class Meta:
        verbose_name = 'Favorite'
        verbose_name_plural = 'Favorites'
        unique_together = ('client', 'barber')
        ordering = ['-created_at']

    client = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='favorites',
        limit_choices_to={'role': 'client'},
    )
    barber = models.ForeignKey(
        'profiles.BarberProfile',
        on_delete=models.CASCADE,
        related_name='favorited_by',
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.client.email} ❤ {self.barber.business_name}"
