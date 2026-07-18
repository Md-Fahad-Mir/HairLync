import logging

import stripe
from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import transaction
from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from drf_yasg.utils import swagger_auto_schema

from . import stripe_service
from .models import SubscriptionPlan, Subscription, StripeWebhookEvent
from .serializers import (
    SubscriptionPlanSerializer, SubscriptionSerializer, SubscriptionCreateSerializer,
    StripeCheckoutSerializer,
)
from Apps.users.permissions import IsBarber, IsAdminUser
from Apps.users.utils import success_response, error_response

logger = logging.getLogger(__name__)
User = get_user_model()


class SubscriptionPlanListView(generics.ListAPIView):
    """List all available subscription plans (public)."""
    serializer_class = SubscriptionPlanSerializer
    permission_classes = [AllowAny]
    queryset = SubscriptionPlan.objects.filter(is_active=True)

    @swagger_auto_schema(
        operation_description="List all available subscription plans.",
        tags=['Subscriptions'],
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class SubscriptionPlanAdminView(generics.CreateAPIView):
    """Create a subscription plan (admin only)."""
    serializer_class = SubscriptionPlanSerializer
    permission_classes = [IsAdminUser]
    queryset = SubscriptionPlan.objects.all()

    @swagger_auto_schema(
        operation_description="Create a new subscription plan (admin only).",
        tags=['Admin'],
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class SubscriptionCreateView(APIView):
    """Manually create + activate a subscription for a barber.

    Admin/internal use only (e.g. comps, support cases, migrations). This
    used to be self-service for any authenticated barber, which meant paid
    access could be granted without any real payment ever taking place.
    Real self-service purchases now go through Stripe Checkout via
    POST /stripe/checkout/, which is verified server-side by a Stripe
    webhook before access is granted.
    """
    permission_classes = [IsAuthenticated, IsAdminUser]

    @swagger_auto_schema(
        operation_description=(
            "Manually create and activate a subscription for a barber "
            "(admin/internal use only — not a real payment flow). "
            "Optionally target a specific barber via `user_id`."
        ),
        request_body=SubscriptionCreateSerializer,
        responses={201: SubscriptionSerializer},
        tags=['Admin'],
    )
    def post(self, request):
        serializer = SubscriptionCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        plan_id = serializer.validated_data['plan_id']
        target_user_id = serializer.validated_data.get('user_id')

        try:
            plan = SubscriptionPlan.objects.get(pk=plan_id, is_active=True)
        except SubscriptionPlan.DoesNotExist:
            return error_response("Subscription plan not found.", status_code=404)

        if target_user_id:
            try:
                target_user = User.objects.get(pk=target_user_id, role='barber')
            except User.DoesNotExist:
                return error_response("Barber user not found.", status_code=404)
        elif request.user.role == 'barber':
            target_user = request.user
        else:
            return error_response("user_id is required to target a barber.", status_code=400)

        # Check for existing active subscription
        active_sub = Subscription.objects.filter(
            user=target_user, status='active'
        ).first()
        if active_sub and active_sub.is_active_subscription:
            return error_response("This user already has an active subscription.", status_code=400)

        subscription = Subscription.objects.create(
            user=target_user,
            plan=plan,
            platform='manual',
            payment_reference=serializer.validated_data.get('payment_reference', ''),
            payment_method=serializer.validated_data.get('payment_method', 'manual'),
            amount_paid=plan.price,
        )

        subscription.activate()

        return success_response(
            data=SubscriptionSerializer(subscription).data,
            message="Subscription activated successfully.",
            status_code=201,
        )


class SubscriptionDetailView(APIView):
    """Get current subscription details or cancel."""
    permission_classes = [IsAuthenticated, IsBarber]

    @swagger_auto_schema(
        operation_description="Get your current subscription details.",
        responses={200: SubscriptionSerializer},
        tags=['Subscriptions'],
    )
    def get(self, request):
        subscription = Subscription.objects.filter(
            user=request.user
        ).order_by('-created_at').first()

        if not subscription:
            return error_response("No subscription found.", status_code=404)

        return success_response(data=SubscriptionSerializer(subscription).data)

    @swagger_auto_schema(
        operation_description="Cancel your current subscription.",
        tags=['Subscriptions'],
    )
    def delete(self, request):
        subscription = Subscription.objects.filter(
            user=request.user, status='active'
        ).first()

        if not subscription:
            return error_response("No active subscription found.", status_code=404)

        subscription.cancel()
        return success_response(message="Subscription cancelled. You will retain access until the end of the billing period.")


class SubscriptionHistoryView(generics.ListAPIView):
    """View subscription history."""
    serializer_class = SubscriptionSerializer
    permission_classes = [IsAuthenticated, IsBarber]

    @swagger_auto_schema(
        operation_description="View your subscription history.",
        tags=['Subscriptions'],
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        return Subscription.objects.filter(user=self.request.user)


class StripeCheckoutView(APIView):
    """Start a real, paid subscription via Stripe Checkout.

    Only accepts an internal plan_id — the Stripe Price ID and price are
    always looked up server-side from SubscriptionPlan; nothing about the
    charge is ever trusted from the client. Access is NOT granted here —
    only Stripe's webhook (checkout.session.completed) activates the
    subscription once payment has actually succeeded.
    """
    permission_classes = [IsAuthenticated, IsBarber]

    @swagger_auto_schema(
        operation_description="Create a Stripe Checkout session for a subscription plan.",
        request_body=StripeCheckoutSerializer,
        tags=['Subscriptions'],
    )
    def post(self, request):
        serializer = StripeCheckoutSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        plan_id = serializer.validated_data['plan_id']

        try:
            plan = SubscriptionPlan.objects.get(pk=plan_id, is_active=True)
        except SubscriptionPlan.DoesNotExist:
            return error_response("Subscription plan not found.", status_code=404)

        active_sub = Subscription.objects.filter(
            user=request.user, status='active'
        ).first()
        if active_sub and active_sub.is_active_subscription:
            return error_response("You already have an active subscription.", status_code=400)

        try:
            session = stripe_service.create_checkout_session(request.user, plan)
        except ValueError as exc:
            return error_response(str(exc), status_code=400)
        except stripe.error.StripeError:
            logger.exception("Stripe error creating checkout session for user %s", request.user.id)
            return error_response(
                "Unable to start checkout with the payment provider right now.",
                status_code=503,
            )

        return success_response(
            data={'checkout_url': session.url, 'session_id': session.id},
            message="Checkout session created.",
            status_code=201,
        )


class StripeBillingPortalView(APIView):
    """Create a Stripe Billing Portal session so a subscribed barber can
    manage/cancel their Stripe subscription or update their card."""
    permission_classes = [IsAuthenticated, IsBarber]

    @swagger_auto_schema(
        operation_description="Create a Stripe billing portal session for the current user.",
        tags=['Subscriptions'],
    )
    def post(self, request):
        try:
            session = stripe_service.create_billing_portal_session(request.user)
        except ValueError as exc:
            return error_response(str(exc), status_code=404)
        except stripe.error.StripeError:
            logger.exception("Stripe error creating billing portal session for user %s", request.user.id)
            return error_response("Unable to open the billing portal right now.", status_code=503)

        return success_response(data={'portal_url': session.url})


class StripeWebhookView(APIView):
    """Receives and verifies Stripe webhook events — the source of truth
    for activating, renewing, cancelling, and expiring Stripe-backed
    subscriptions (never the success-page redirect).

    Every event ID is recorded exactly once (StripeWebhookEvent, unique
    constraint) inside the same transaction as the event's side effects,
    so duplicate deliveries of the same event short-circuit and cannot
    activate or update a subscription twice.
    """
    authentication_classes = []
    permission_classes = [AllowAny]

    def post(self, request):
        if not settings.STRIPE_WEBHOOK_SECRET:
            logger.error("STRIPE_WEBHOOK_SECRET is not configured; rejecting webhook.")
            return error_response("Webhook is not configured.", status_code=503)

        payload = request.body
        sig_header = request.META.get('HTTP_STRIPE_SIGNATURE', '')

        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
            )
        except ValueError:
            return error_response("Invalid payload.", status_code=400)
        except stripe.error.SignatureVerificationError:
            return error_response("Invalid signature.", status_code=400)

        event_id = event['id']
        event_type = event['type']

        try:
            with transaction.atomic():
                event_row, created = (
                    StripeWebhookEvent.objects.select_for_update()
                    .get_or_create(
                        event_id=event_id,
                        defaults={'event_type': event_type, 'status': 'processing'},
                    )
                )
                if not created:
                    return success_response(message="Event already processed.")

                stripe_service.process_event(event)

                event_row.status = 'processed'
                event_row.save(update_fields=['status'])
        except Exception:
            # The whole transaction (including the event-claim row) rolls
            # back, so a retried delivery from Stripe will be reprocessed
            # cleanly rather than being silently swallowed as a duplicate.
            logger.exception("Failed processing Stripe event %s (%s)", event_id, event_type)
            return error_response("Webhook processing failed.", status_code=500)

        return success_response(message="Webhook processed.")
