from unittest.mock import patch, MagicMock

from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from django.utils import timezone
from rest_framework.test import APIClient
import stripe

from Apps.subscriptions.models import (
    SubscriptionPlan, Subscription, StripeCustomer, StripeWebhookEvent,
)

User = get_user_model()


def fake_stripe_subscription(
    sub_id, customer_id, status='active', metadata=None,
    cancel_at_period_end=False, period_start=None, period_end=None,
):
    """Build a plain-dict stand-in for a stripe.Subscription object. Only
    key/`.get()` access is used anywhere in stripe_service.py, so a dict is
    sufficient and avoids any real network calls to Stripe."""
    now = timezone.now()
    return {
        'id': sub_id,
        'customer': customer_id,
        'status': status,
        'metadata': metadata or {},
        'cancel_at_period_end': cancel_at_period_end,
        'current_period_start': int((period_start or now).timestamp()),
        'current_period_end': int((period_end or now + timezone.timedelta(days=30)).timestamp()),
    }


class StripeCheckoutViewTests(TestCase):
    def setUp(self):
        self.api = APIClient()
        self.barber = User.objects.create_user(
            email='barber@t.com', password='p', is_active=True, role='barber'
        )
        self.plan = SubscriptionPlan.objects.create(
            name='Pro Monthly', billing_cycle='monthly', price=29.99,
            stripe_price_id='price_test_123',
        )
        self.api.force_authenticate(user=self.barber)

    def test_requires_authentication(self):
        anon = APIClient()
        r = anon.post('/api/v1/subscriptions/stripe/checkout/', {'plan_id': self.plan.id}, format='json')
        self.assertEqual(r.status_code, 401)

    def test_plan_not_found(self):
        r = self.api.post('/api/v1/subscriptions/stripe/checkout/', {'plan_id': 99999}, format='json')
        self.assertEqual(r.status_code, 404)

    def test_plan_without_stripe_price_id_rejected(self):
        plan = SubscriptionPlan.objects.create(name='No Stripe Plan', billing_cycle='monthly', price=10)
        r = self.api.post('/api/v1/subscriptions/stripe/checkout/', {'plan_id': plan.id}, format='json')
        self.assertEqual(r.status_code, 400)

    def test_already_subscribed_rejected(self):
        sub = Subscription.objects.create(user=self.barber, plan=self.plan, amount_paid=29.99)
        sub.activate()
        r = self.api.post('/api/v1/subscriptions/stripe/checkout/', {'plan_id': self.plan.id}, format='json')
        self.assertEqual(r.status_code, 400)

    @patch('Apps.subscriptions.stripe_service.stripe.checkout.Session.create')
    @patch('Apps.subscriptions.stripe_service.stripe.Customer.create')
    def test_checkout_session_created_ignores_client_price(self, mock_customer_create, mock_session_create):
        mock_customer_create.return_value = {'id': 'cus_test_1'}
        mock_session_create.return_value = MagicMock(id='cs_test_1', url='https://checkout.stripe.com/cs_test_1')

        # Client tries to smuggle a different price/amount — must be ignored.
        r = self.api.post(
            '/api/v1/subscriptions/stripe/checkout/',
            {'plan_id': self.plan.id, 'price': '0.01', 'amount': 1},
            format='json',
        )

        self.assertEqual(r.status_code, 201)
        self.assertEqual(r.json()['data']['checkout_url'], 'https://checkout.stripe.com/cs_test_1')
        self.assertEqual(r.json()['data']['session_id'], 'cs_test_1')

        # The Stripe Price used must be the one stored server-side on the plan.
        _, kwargs = mock_session_create.call_args
        self.assertEqual(kwargs['line_items'], [{'price': 'price_test_123', 'quantity': 1}])
        self.assertEqual(kwargs['mode'], 'subscription')
        self.assertTrue(StripeCustomer.objects.filter(user=self.barber, stripe_customer_id='cus_test_1').exists())

    @patch('Apps.subscriptions.stripe_service.stripe.checkout.Session.create')
    def test_checkout_reuses_existing_stripe_customer(self, mock_session_create):
        StripeCustomer.objects.create(user=self.barber, stripe_customer_id='cus_existing')
        mock_session_create.return_value = MagicMock(id='cs_test_2', url='https://checkout.stripe.com/cs_test_2')

        with patch('Apps.subscriptions.stripe_service.stripe.Customer.create') as mock_customer_create:
            r = self.api.post('/api/v1/subscriptions/stripe/checkout/', {'plan_id': self.plan.id}, format='json')
            mock_customer_create.assert_not_called()

        self.assertEqual(r.status_code, 201)
        _, kwargs = mock_session_create.call_args
        self.assertEqual(kwargs['customer'], 'cus_existing')


class StripeBillingPortalViewTests(TestCase):
    def setUp(self):
        self.api = APIClient()
        self.barber = User.objects.create_user(
            email='barber2@t.com', password='p', is_active=True, role='barber'
        )
        self.api.force_authenticate(user=self.barber)

    def test_no_stripe_customer_returns_404(self):
        r = self.api.post('/api/v1/subscriptions/stripe/billing-portal/')
        self.assertEqual(r.status_code, 404)

    @patch('Apps.subscriptions.stripe_service.stripe.billing_portal.Session.create')
    def test_billing_portal_session_created(self, mock_portal_create):
        StripeCustomer.objects.create(user=self.barber, stripe_customer_id='cus_test_9')
        mock_portal_create.return_value = MagicMock(url='https://billing.stripe.com/session_1')

        r = self.api.post('/api/v1/subscriptions/stripe/billing-portal/')

        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.json()['data']['portal_url'], 'https://billing.stripe.com/session_1')
        mock_portal_create.assert_called_once_with(customer='cus_test_9', return_url=mock_portal_create.call_args.kwargs['return_url'])


@override_settings(STRIPE_WEBHOOK_SECRET='whsec_test_dummy')
class StripeWebhookViewTests(TestCase):
    def setUp(self):
        self.api = APIClient()
        self.barber = User.objects.create_user(
            email='barber3@t.com', password='p', is_active=True, role='barber'
        )
        self.plan = SubscriptionPlan.objects.create(
            name='Pro Yearly', billing_cycle='yearly', price=199,
            stripe_price_id='price_test_yearly',
        )

    def _post_event(self, event):
        with patch('Apps.subscriptions.views.stripe.Webhook.construct_event', return_value=event):
            return self.api.post(
                '/api/v1/subscriptions/stripe/webhook/',
                data='{}',
                content_type='application/json',
                HTTP_STRIPE_SIGNATURE='test_sig',
            )

    def test_invalid_signature_rejected(self):
        with patch(
            'Apps.subscriptions.views.stripe.Webhook.construct_event',
            side_effect=stripe.error.SignatureVerificationError('bad sig', 'sig_header'),
        ):
            r = self.api.post(
                '/api/v1/subscriptions/stripe/webhook/',
                data='{}',
                content_type='application/json',
                HTTP_STRIPE_SIGNATURE='bad',
            )
        self.assertEqual(r.status_code, 400)

    def test_unconfigured_secret_rejected(self):
        with self.settings(STRIPE_WEBHOOK_SECRET=''):
            r = self.api.post(
                '/api/v1/subscriptions/stripe/webhook/',
                data='{}',
                content_type='application/json',
                HTTP_STRIPE_SIGNATURE='whatever',
            )
        self.assertEqual(r.status_code, 503)

    @patch('Apps.subscriptions.stripe_service.stripe.Subscription.retrieve')
    def test_checkout_completed_activates_subscription(self, mock_retrieve):
        stripe_sub_id = 'sub_checkout_1'
        mock_retrieve.return_value = fake_stripe_subscription(
            stripe_sub_id, 'cus_checkout_1', status='active',
            metadata={'user_id': str(self.barber.id), 'plan_id': str(self.plan.id)},
        )
        event = {
            'id': 'evt_checkout_1',
            'type': 'checkout.session.completed',
            'data': {'object': {
                'id': 'cs_1',
                'mode': 'subscription',
                'subscription': stripe_sub_id,
                'customer': 'cus_checkout_1',
                'metadata': {'user_id': str(self.barber.id), 'plan_id': str(self.plan.id)},
            }},
        }

        r = self._post_event(event)

        self.assertEqual(r.status_code, 200)
        sub = Subscription.objects.get(stripe_subscription_id=stripe_sub_id)
        self.assertEqual(sub.status, 'active')
        self.assertEqual(sub.platform, 'stripe')
        self.assertEqual(sub.user_id, self.barber.id)
        self.barber.refresh_from_db()
        self.assertTrue(self.barber.is_subscribed())
        self.assertTrue(
            StripeWebhookEvent.objects.filter(event_id='evt_checkout_1', status='processed').exists()
        )

    @patch('Apps.subscriptions.stripe_service.stripe.Subscription.retrieve')
    def test_duplicate_webhook_delivery_is_idempotent(self, mock_retrieve):
        stripe_sub_id = 'sub_dup_1'
        mock_retrieve.return_value = fake_stripe_subscription(
            stripe_sub_id, 'cus_dup_1', status='active',
            metadata={'user_id': str(self.barber.id), 'plan_id': str(self.plan.id)},
        )
        event = {
            'id': 'evt_dup_1',
            'type': 'checkout.session.completed',
            'data': {'object': {
                'id': 'cs_dup_1',
                'mode': 'subscription',
                'subscription': stripe_sub_id,
                'customer': 'cus_dup_1',
                'metadata': {'user_id': str(self.barber.id), 'plan_id': str(self.plan.id)},
            }},
        }

        r1 = self._post_event(event)
        r2 = self._post_event(event)

        self.assertEqual(r1.status_code, 200)
        self.assertEqual(r2.status_code, 200)
        self.assertEqual(Subscription.objects.filter(stripe_subscription_id=stripe_sub_id).count(), 1)
        self.assertEqual(StripeWebhookEvent.objects.filter(event_id='evt_dup_1').count(), 1)
        # retrieve() (and therefore activation logic) only ran once — the
        # second delivery short-circuited on the already-processed event.
        self.assertEqual(mock_retrieve.call_count, 1)

    def test_subscription_deleted_revokes_access(self):
        sub = Subscription.objects.create(
            user=self.barber, plan=self.plan, platform='stripe',
            stripe_subscription_id='sub_del_1', stripe_customer_id='cus_del_1',
        )
        sub.activate()
        self.barber.refresh_from_db()
        self.assertTrue(self.barber.is_subscribed())

        event = {
            'id': 'evt_del_1',
            'type': 'customer.subscription.deleted',
            'data': {'object': fake_stripe_subscription('sub_del_1', 'cus_del_1', status='canceled')},
        }
        r = self._post_event(event)

        self.assertEqual(r.status_code, 200)
        sub.refresh_from_db()
        self.assertEqual(sub.status, 'expired')
        self.barber.refresh_from_db()
        self.assertFalse(self.barber.is_subscribed())
        self.assertFalse(self.barber.paid_user)

    def test_subscription_cancel_at_period_end_keeps_access(self):
        sub = Subscription.objects.create(
            user=self.barber, plan=self.plan, platform='stripe',
            stripe_subscription_id='sub_cape_1', stripe_customer_id='cus_cape_1',
        )
        sub.activate()

        event = {
            'id': 'evt_cape_1',
            'type': 'customer.subscription.updated',
            'data': {'object': fake_stripe_subscription(
                'sub_cape_1', 'cus_cape_1', status='active', cancel_at_period_end=True,
            )},
        }
        r = self._post_event(event)

        self.assertEqual(r.status_code, 200)
        sub.refresh_from_db()
        self.assertEqual(sub.status, 'cancelled')
        self.barber.refresh_from_db()
        # Access continues until period end, matching the pre-existing
        # manual-cancellation semantics.
        self.assertTrue(self.barber.is_subscribed())

    def test_invoice_payment_failed_records_error_without_revoking_access(self):
        sub = Subscription.objects.create(
            user=self.barber, plan=self.plan, platform='stripe',
            stripe_subscription_id='sub_fail_1', stripe_customer_id='cus_fail_1',
        )
        sub.activate()

        event = {
            'id': 'evt_fail_1',
            'type': 'invoice.payment_failed',
            'data': {'object': {'id': 'in_fail_1', 'subscription': 'sub_fail_1'}},
        }
        r = self._post_event(event)

        self.assertEqual(r.status_code, 200)
        sub.refresh_from_db()
        self.assertTrue(sub.last_payment_error)
        self.assertIsNotNone(sub.payment_failed_at)
        self.assertEqual(sub.status, 'active')
        self.barber.refresh_from_db()
        self.assertTrue(self.barber.is_subscribed())

    @patch('Apps.subscriptions.stripe_service.stripe.Subscription.retrieve')
    def test_invoice_paid_extends_period(self, mock_retrieve):
        sub = Subscription.objects.create(
            user=self.barber, plan=self.plan, platform='stripe',
            stripe_subscription_id='sub_renew_1', stripe_customer_id='cus_renew_1',
        )
        sub.activate()
        original_end = sub.end_date

        # Plan is yearly, so activate() defaults end_date to +365 days;
        # push the renewed period further out than that to prove it moved.
        new_period_end = timezone.now() + timezone.timedelta(days=400)
        mock_retrieve.return_value = fake_stripe_subscription(
            'sub_renew_1', 'cus_renew_1', status='active', period_end=new_period_end,
        )
        event = {
            'id': 'evt_renew_1',
            'type': 'invoice.paid',
            'data': {'object': {'id': 'in_renew_1', 'subscription': 'sub_renew_1'}},
        }
        r = self._post_event(event)

        self.assertEqual(r.status_code, 200)
        sub.refresh_from_db()
        self.assertGreater(sub.end_date, original_end)
        self.assertEqual(sub.status, 'active')

    def test_unresolvable_metadata_is_skipped_not_errored(self):
        """An event for a subscription we can't map to a local user/plan
        should be logged and ignored, not raise / 500."""
        event = {
            'id': 'evt_unknown_1',
            'type': 'customer.subscription.updated',
            'data': {'object': fake_stripe_subscription(
                'sub_unknown_1', 'cus_unknown_1', status='active', metadata={},
            )},
        }
        r = self._post_event(event)
        self.assertEqual(r.status_code, 200)
        self.assertFalse(Subscription.objects.filter(stripe_subscription_id='sub_unknown_1').exists())


class ManualSubscribeSecurityTests(TestCase):
    """The manual /subscribe/ endpoint used to let any authenticated
    barber grant themselves paid access for free. It is now admin/internal
    use only."""

    def setUp(self):
        self.api = APIClient()
        self.barber = User.objects.create_user(
            email='barber4@t.com', password='p', is_active=True, role='barber'
        )
        self.other_barber = User.objects.create_user(
            email='barber5@t.com', password='p', is_active=True, role='barber'
        )
        self.admin = User.objects.create_user(
            email='admin@t.com', password='p', is_active=True, role='admin'
        )
        self.plan = SubscriptionPlan.objects.create(
            name='Manual Plan', billing_cycle='monthly', price=15,
        )

    def test_barber_can_no_longer_self_activate(self):
        self.api.force_authenticate(user=self.barber)
        r = self.api.post('/api/v1/subscriptions/subscribe/', {'plan_id': self.plan.id}, format='json')
        self.assertEqual(r.status_code, 403)
        self.barber.refresh_from_db()
        self.assertFalse(self.barber.is_subscribed())

    def test_unauthenticated_rejected(self):
        r = self.api.post('/api/v1/subscriptions/subscribe/', {'plan_id': self.plan.id}, format='json')
        self.assertEqual(r.status_code, 401)

    def test_admin_can_activate_for_a_target_barber(self):
        self.api.force_authenticate(user=self.admin)
        r = self.api.post(
            '/api/v1/subscriptions/subscribe/',
            {'plan_id': self.plan.id, 'user_id': self.other_barber.id},
            format='json',
        )
        self.assertEqual(r.status_code, 201)
        self.other_barber.refresh_from_db()
        self.assertTrue(self.other_barber.is_subscribed())

    def test_admin_without_user_id_and_not_a_barber_is_rejected(self):
        self.api.force_authenticate(user=self.admin)
        r = self.api.post('/api/v1/subscriptions/subscribe/', {'plan_id': self.plan.id}, format='json')
        self.assertEqual(r.status_code, 400)

    def test_admin_targeting_unknown_barber_404(self):
        self.api.force_authenticate(user=self.admin)
        r = self.api.post(
            '/api/v1/subscriptions/subscribe/',
            {'plan_id': self.plan.id, 'user_id': 999999},
            format='json',
        )
        self.assertEqual(r.status_code, 404)
