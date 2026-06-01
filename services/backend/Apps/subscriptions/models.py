from django.db import models
from django.conf import settings
from django.utils import timezone
from datetime import timedelta


# ------------------------------------------------------------------------------
# SUBSCRIPTION PLAN
# ------------------------------------------------------------------------------
class SubscriptionPlan(models.Model):
    """Available subscription plans for barbers."""

    class Meta:
        verbose_name = 'Subscription Plan'
        verbose_name_plural = 'Subscription Plans'
        ordering = ['price']

    BILLING_CHOICES = [
        ('monthly', 'Monthly'),
        ('yearly', 'Yearly'),
    ]

    name = models.CharField(max_length=100, unique=True)
    billing_cycle = models.CharField(max_length=10, choices=BILLING_CHOICES)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField(blank=True, default='')
    features = models.JSONField(
        default=list,
        blank=True,
        help_text='List of features included: ["feature1", "feature2"]'
    )

    # Limits
    max_employees = models.PositiveIntegerField(default=5)
    max_portfolio_images = models.PositiveIntegerField(default=20)
    max_services = models.PositiveIntegerField(default=50)
    has_ai_recommendations = models.BooleanField(default=False)
    has_educational_content = models.BooleanField(default=False)
    has_analytics = models.BooleanField(default=False)

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.billing_cycle}) - ${self.price}"


# ------------------------------------------------------------------------------
# SUBSCRIPTION
# ------------------------------------------------------------------------------
class Subscription(models.Model):
    """Active subscription for a barber user."""

    class Meta:
        verbose_name = 'Subscription'
        verbose_name_plural = 'Subscriptions'
        ordering = ['-created_at']

    STATUS_CHOICES = [
        ('active', 'Active'),
        ('expired', 'Expired'),
        ('cancelled', 'Cancelled'),
        ('pending', 'Pending Payment'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='subscriptions',
        limit_choices_to={'role': 'barber'},
    )
    plan = models.ForeignKey(
        SubscriptionPlan,
        on_delete=models.PROTECT,
        related_name='subscriptions',
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    start_date = models.DateTimeField(null=True, blank=True)
    end_date = models.DateTimeField(null=True, blank=True)

    # Payment tracking (integration-ready)
    payment_reference = models.CharField(max_length=255, blank=True, default='')
    payment_method = models.CharField(max_length=50, blank=True, default='')
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    auto_renew = models.BooleanField(default=True)
    cancelled_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.email} - {self.plan.name} ({self.status})"

    @property
    def is_active_subscription(self):
        """Check if subscription is currently active."""
        if self.status != 'active':
            return False
        if self.end_date and self.end_date < timezone.now():
            return False
        return True

    def activate(self):
        """Activate the subscription."""
        now = timezone.now()
        self.status = 'active'
        self.start_date = now
        if self.plan.billing_cycle == 'monthly':
            self.end_date = now + timedelta(days=30)
        else:
            self.end_date = now + timedelta(days=365)
        self.save()

        # Update user's subscription fields
        self.user.paid_user = True
        self.user.current_plan = self.plan.billing_cycle
        self.user.current_period_start = self.start_date
        self.user.current_period_end = self.end_date
        self.user.save(update_fields=[
            'paid_user', 'current_plan', 'current_period_start', 'current_period_end'
        ])

    def cancel(self):
        """Cancel the subscription."""
        self.status = 'cancelled'
        self.auto_renew = False
        self.cancelled_at = timezone.now()
        self.save()

    def expire(self):
        """Mark subscription as expired."""
        self.status = 'expired'
        self.save()

        self.user.paid_user = False
        self.user.current_plan = 'free'
        self.user.current_period_start = None
        self.user.current_period_end = None
        self.user.save(update_fields=[
            'paid_user', 'current_plan', 'current_period_start', 'current_period_end'
        ])
