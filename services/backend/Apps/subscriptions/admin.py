from django.contrib import admin
from .models import SubscriptionPlan, Subscription, StripeCustomer, StripeWebhookEvent


@admin.register(SubscriptionPlan)
class SubscriptionPlanAdmin(admin.ModelAdmin):
    list_display = ('name', 'billing_cycle', 'price', 'stripe_price_id', 'max_employees', 'is_active')
    list_filter = ('billing_cycle', 'is_active')
    list_editable = ('is_active',)
    search_fields = ('name', 'stripe_price_id', 'stripe_product_id')


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = (
        'user', 'plan', 'status', 'platform', 'start_date', 'end_date',
        'amount_paid', 'payment_failed_at',
    )
    list_filter = ('status', 'platform', 'plan')
    search_fields = ('user__email', 'stripe_customer_id', 'stripe_subscription_id', 'payment_reference')
    raw_id_fields = ('user',)


@admin.register(StripeCustomer)
class StripeCustomerAdmin(admin.ModelAdmin):
    list_display = ('user', 'stripe_customer_id', 'created_at')
    search_fields = ('user__email', 'stripe_customer_id')
    raw_id_fields = ('user',)


@admin.register(StripeWebhookEvent)
class StripeWebhookEventAdmin(admin.ModelAdmin):
    list_display = ('event_type', 'event_id', 'status', 'received_at')
    list_filter = ('status', 'event_type')
    search_fields = ('event_id',)
    readonly_fields = ('event_id', 'event_type', 'received_at')
