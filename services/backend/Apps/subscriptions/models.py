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

    # Stripe mapping (integration-ready)
    stripe_price_id = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        unique=True,
        default=None,
        help_text='Stripe Price ID (price_...) that Stripe Checkout should charge for this plan.',
    )
    stripe_product_id = models.CharField(max_length=255, blank=True, default='')

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
        indexes = [
            models.Index(fields=['user', 'status']),
        ]

    STATUS_CHOICES = [
        ('active', 'Active'),
        ('expired', 'Expired'),
        ('cancelled', 'Cancelled'),
        ('pending', 'Pending Payment'),
    ]

    PLATFORM_CHOICES = [
        ('manual', 'Manual'),
        ('stripe', 'Stripe'),
        ('apple', 'Apple App Store'),
        ('google', 'Google Play'),
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
    platform = models.CharField(
        max_length=20, choices=PLATFORM_CHOICES, default='manual', db_index=True,
        help_text='Which payment channel this subscription record came from.',
    )
    payment_reference = models.CharField(max_length=255, blank=True, default='')
    payment_method = models.CharField(max_length=50, blank=True, default='')
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    # Stripe-specific identifiers (blank/unused for manual/apple/google records)
    stripe_customer_id = models.CharField(max_length=255, blank=True, default='', db_index=True)
    stripe_subscription_id = models.CharField(max_length=255, null=True, blank=True, unique=True)
    stripe_checkout_session_id = models.CharField(max_length=255, blank=True, default='')
    last_payment_error = models.CharField(max_length=500, blank=True, default='')
    payment_failed_at = models.DateTimeField(null=True, blank=True)

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

    def activate(self, start_date=None, end_date=None):
        """Activate the subscription.

        `start_date`/`end_date` let a real payment platform (e.g. Stripe)
        supply the authoritative billing period instead of the default
        now+30/365-day estimate used by the manual flow. Called with no
        arguments this behaves exactly as before.
        """
        now = timezone.now()
        self.status = 'active'
        self.start_date = start_date or now
        if end_date:
            self.end_date = end_date
        elif self.plan.billing_cycle == 'monthly':
            self.end_date = self.start_date + timedelta(days=30)
        else:
            self.end_date = self.start_date + timedelta(days=365)
        self.last_payment_error = ''
        self.payment_failed_at = None
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
        """Cancel the subscription.

        Access is intentionally left untouched (paid_user/current_period_end
        on the user are not modified), so the user keeps access until the
        stored period end, matching how the existing manual-cancel API has
        always behaved.
        """
        self.status = 'cancelled'
        self.auto_renew = False
        self.cancelled_at = timezone.now()
        self.save()

    def expire(self):
        """Mark subscription as expired and revoke the user's paid access."""
        self.status = 'expired'
        self.save()

        self.user.paid_user = False
        self.user.current_plan = 'free'
        self.user.current_period_start = None
        self.user.current_period_end = None
        self.user.save(update_fields=[
            'paid_user', 'current_plan', 'current_period_start', 'current_period_end'
        ])

    def mark_payment_failed(self, message=''):
        """Record a failed payment/renewal without revoking access.

        Stripe retries failed invoices automatically (dunning); a
        subscription is only expired once Stripe itself reports the
        underlying subscription as canceled/unpaid.
        """
        self.last_payment_error = (message or 'Payment failed.')[:500]
        self.payment_failed_at = timezone.now()
        self.save(update_fields=['last_payment_error', 'payment_failed_at'])


# ------------------------------------------------------------------------------
# STRIPE CUSTOMER MAPPING
# ------------------------------------------------------------------------------
class StripeCustomer(models.Model):
    """Maps a HairLync user to their Stripe Customer object."""

    class Meta:
        verbose_name = 'Stripe Customer'
        verbose_name_plural = 'Stripe Customers'

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='stripe_customer',
    )
    stripe_customer_id = models.CharField(max_length=255, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.email} -> {self.stripe_customer_id}"


# ------------------------------------------------------------------------------
# STRIPE WEBHOOK EVENT LEDGER (idempotency)
# ------------------------------------------------------------------------------
class StripeWebhookEvent(models.Model):
    """Records processed Stripe webhook event IDs so duplicate deliveries
    (Stripe sends events at-least-once) cannot activate or update a
    subscription twice."""

    class Meta:
        verbose_name = 'Stripe Webhook Event'
        verbose_name_plural = 'Stripe Webhook Events'
        ordering = ['-received_at']

    STATUS_CHOICES = [
        ('processing', 'Processing'),
        ('processed', 'Processed'),
        ('failed', 'Failed'),
    ]

    event_id = models.CharField(max_length=255, unique=True, db_index=True)
    event_type = models.CharField(max_length=100)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='processing')
    error_message = models.TextField(blank=True, default='')
    received_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.event_type} ({self.event_id})"
