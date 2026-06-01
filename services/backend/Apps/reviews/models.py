from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator


# ------------------------------------------------------------------------------
# REVIEW
# ------------------------------------------------------------------------------
class Review(models.Model):
    """Client review and rating for a barber."""

    class Meta:
        verbose_name = 'Review'
        verbose_name_plural = 'Reviews'
        ordering = ['-created_at']
        unique_together = ('client', 'barber', 'booking')
        indexes = [
            models.Index(fields=['barber', '-created_at']),
        ]

    client = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='reviews_given',
        limit_choices_to={'role': 'client'},
    )
    barber = models.ForeignKey(
        'profiles.BarberProfile',
        on_delete=models.CASCADE,
        related_name='reviews',
    )
    booking = models.OneToOneField(
        'bookings.Booking',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='review',
    )

    rating = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text='Rating from 1 to 5 stars',
    )
    comment = models.TextField(blank=True, default='')
    barber_response = models.TextField(blank=True, default='')
    barber_responded_at = models.DateTimeField(null=True, blank=True)

    # Moderation
    is_approved = models.BooleanField(default=True)
    is_flagged = models.BooleanField(default=False)
    flag_reason = models.TextField(blank=True, default='')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Review by {self.client.email} for {self.barber.business_name}: {self.rating}★"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Update barber's average rating
        self._update_barber_rating()

    def delete(self, *args, **kwargs):
        barber = self.barber
        super().delete(*args, **kwargs)
        self._update_barber_rating(barber=barber)

    def _update_barber_rating(self, barber=None):
        """Recalculate and update the barber's average rating."""
        barber = barber or self.barber
        reviews = Review.objects.filter(barber=barber, is_approved=True)
        total = reviews.count()
        if total > 0:
            avg = reviews.aggregate(avg=models.Avg('rating'))['avg']
            barber.average_rating = round(avg, 2)
        else:
            barber.average_rating = 0.00
        barber.total_reviews = total
        barber.save(update_fields=['average_rating', 'total_reviews'])
