"""Stripe SDK integration for the subscriptions app.

Keeps all Stripe API calls and webhook-event interpretation in one place so
views.py stays a thin HTTP layer. Nothing here trusts client-supplied price,
amount, or status data — plans and prices are always looked up from the
database, and subscription state is always derived from Stripe's own API/
webhook payloads.
"""
import logging
from datetime import datetime, timezone as dt_timezone

import stripe
from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import transaction

from .models import Subscription, SubscriptionPlan, StripeCustomer

logger = logging.getLogger(__name__)

stripe.api_key = settings.STRIPE_SECRET_KEY


def _ts_to_datetime(timestamp):
    if timestamp is None:
        return None
    return datetime.fromtimestamp(timestamp, tz=dt_timezone.utc)


def get_or_create_stripe_customer(user):
    """Return the Stripe Customer ID for a user, creating one if needed."""
    existing = StripeCustomer.objects.filter(user=user).first()
    if existing:
        return existing.stripe_customer_id

    customer = stripe.Customer.create(
        email=user.email,
        name=user.full_name or user.email,
        metadata={'user_id': str(user.id)},
    )
    stripe_customer, _ = StripeCustomer.objects.get_or_create(
        user=user, defaults={'stripe_customer_id': customer['id']}
    )
    return stripe_customer.stripe_customer_id


def create_checkout_session(user, plan):
    """Create a Stripe Checkout Session (subscription mode) for the given
    internal plan. Never accepts a price/amount from the caller — the
    Stripe Price ID is always read from `plan.stripe_price_id` in the DB."""
    if not plan.stripe_price_id:
        raise ValueError('This plan is not configured for Stripe checkout.')

    customer_id = get_or_create_stripe_customer(user)
    metadata = {'user_id': str(user.id), 'plan_id': str(plan.id)}

    session = stripe.checkout.Session.create(
        mode='subscription',
        customer=customer_id,
        line_items=[{'price': plan.stripe_price_id, 'quantity': 1}],
        success_url=settings.STRIPE_CHECKOUT_SUCCESS_URL + '?session_id={CHECKOUT_SESSION_ID}',
        cancel_url=settings.STRIPE_CHECKOUT_CANCEL_URL,
        client_reference_id=str(user.id),
        metadata=metadata,
        subscription_data={'metadata': metadata},
    )
    return session


def create_billing_portal_session(user):
    """Create a Stripe Billing Portal session for a user that already has a
    Stripe customer record."""
    stripe_customer = StripeCustomer.objects.filter(user=user).first()
    if not stripe_customer:
        raise ValueError('No Stripe customer found for this user.')

    session = stripe.billing_portal.Session.create(
        customer=stripe_customer.stripe_customer_id,
        return_url=settings.STRIPE_BILLING_PORTAL_RETURN_URL,
    )
    return session


def _resolve_user_and_plan(metadata, fallback_customer_id=None):
    """Resolve the internal user/plan a Stripe object belongs to, using the
    metadata we attach at checkout-session creation time, falling back to
    the local Stripe customer mapping if metadata is missing."""
    User = get_user_model()
    metadata = metadata or {}
    user_id = metadata.get('user_id')
    plan_id = metadata.get('plan_id')

    user = User.objects.filter(pk=user_id).first() if user_id else None
    plan = SubscriptionPlan.objects.filter(pk=plan_id).first() if plan_id else None

    if user is None and fallback_customer_id:
        stripe_customer = StripeCustomer.objects.filter(
            stripe_customer_id=fallback_customer_id
        ).select_related('user').first()
        if stripe_customer:
            user = stripe_customer.user

    return user, plan


def _upsert_subscription_from_stripe(stripe_subscription, metadata=None):
    """Create or update the local Subscription row to match the state of a
    Stripe Subscription object. Used for checkout completion, subscription
    created/updated/deleted, and invoice-driven renewals — all funnel
    through here so the local record always mirrors Stripe's own view."""
    stripe_sub_id = stripe_subscription['id']
    stripe_customer_id = stripe_subscription['customer']
    metadata = metadata or stripe_subscription.get('metadata') or {}

    with transaction.atomic():
        subscription = (
            Subscription.objects.select_for_update()
            .filter(stripe_subscription_id=stripe_sub_id)
            .first()
        )

        if subscription is None:
            user, plan = _resolve_user_and_plan(metadata, fallback_customer_id=stripe_customer_id)
            if user is None or plan is None:
                logger.error(
                    "Stripe subscription %s has no resolvable user/plan "
                    "(metadata=%s, customer=%s); skipping.",
                    stripe_sub_id, metadata, stripe_customer_id,
                )
                return None

            StripeCustomer.objects.get_or_create(
                user=user, defaults={'stripe_customer_id': stripe_customer_id}
            )

            subscription = Subscription.objects.create(
                user=user,
                plan=plan,
                platform='stripe',
                status='pending',
                stripe_customer_id=stripe_customer_id,
                stripe_subscription_id=stripe_sub_id,
                payment_method='stripe',
                payment_reference=stripe_sub_id,
                amount_paid=plan.price,
            )

        period_start = _ts_to_datetime(stripe_subscription.get('current_period_start'))
        period_end = _ts_to_datetime(stripe_subscription.get('current_period_end'))
        stripe_status = stripe_subscription.get('status')
        cancel_at_period_end = bool(stripe_subscription.get('cancel_at_period_end'))

        if stripe_status in ('active', 'trialing'):
            subscription.activate(start_date=period_start, end_date=period_end)
            if cancel_at_period_end:
                # User has requested cancellation but keeps access until the
                # period ends — mirrors the existing manual cancel() semantics.
                subscription.cancel()
        elif stripe_status in ('canceled', 'unpaid', 'incomplete_expired'):
            subscription.expire()
        elif stripe_status == 'past_due':
            subscription.mark_payment_failed('Stripe reported the subscription as past_due.')
        else:
            logger.info("Unhandled Stripe subscription status '%s' for %s", stripe_status, stripe_sub_id)

        return subscription


def handle_checkout_session_completed(session):
    if session.get('mode') != 'subscription':
        return
    stripe_subscription_id = session.get('subscription')
    if not stripe_subscription_id:
        return
    stripe_subscription = stripe.Subscription.retrieve(stripe_subscription_id)
    _upsert_subscription_from_stripe(stripe_subscription, metadata=session.get('metadata'))


def handle_subscription_event(stripe_subscription):
    """Shared handler for customer.subscription.created/updated/deleted —
    Stripe's event payload for all three is the full Subscription object,
    and its `status` field already tells us what to do."""
    _upsert_subscription_from_stripe(stripe_subscription)


def handle_invoice_paid(invoice):
    stripe_subscription_id = invoice.get('subscription')
    if not stripe_subscription_id:
        return
    stripe_subscription = stripe.Subscription.retrieve(stripe_subscription_id)
    _upsert_subscription_from_stripe(stripe_subscription)


def handle_invoice_payment_failed(invoice):
    stripe_subscription_id = invoice.get('subscription')
    if not stripe_subscription_id:
        return
    with transaction.atomic():
        subscription = (
            Subscription.objects.select_for_update()
            .filter(stripe_subscription_id=stripe_subscription_id)
            .first()
        )
        if subscription is None:
            logger.warning(
                "invoice.payment_failed for unknown Stripe subscription %s",
                stripe_subscription_id,
            )
            return
        subscription.mark_payment_failed(
            f"Payment failed for invoice {invoice.get('id', '')}."
        )


EVENT_HANDLERS = {
    'checkout.session.completed': handle_checkout_session_completed,
    'customer.subscription.created': handle_subscription_event,
    'customer.subscription.updated': handle_subscription_event,
    'customer.subscription.deleted': handle_subscription_event,
    'invoice.paid': handle_invoice_paid,
    'invoice.payment_failed': handle_invoice_payment_failed,
}


def process_event(event):
    """Dispatch a verified Stripe event to its handler. Unknown event types
    are logged and ignored (Stripe sends many events we don't act on)."""
    handler = EVENT_HANDLERS.get(event['type'])
    if handler is None:
        logger.info("Ignoring unhandled Stripe event type: %s", event['type'])
        return
    handler(event['data']['object'])
