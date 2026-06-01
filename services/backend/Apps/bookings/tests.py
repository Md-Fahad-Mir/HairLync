from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from Apps.profiles.models import BarberProfile
from Apps.services.models import ServiceCategory, Service
from Apps.bookings.models import Booking, TimeSlot
from Apps.reviews.models import Review
from Apps.favorites.models import Favorite
from Apps.subscriptions.models import SubscriptionPlan, Subscription
import datetime

User = get_user_model()


class BookingTests(TestCase):
    def setUp(self):
        self.api = APIClient()
        self.client_user = User.objects.create_user(
            email='cl@t.com', password='p', is_active=True, role='client'
        )
        self.barber_user = User.objects.create_user(
            email='br@t.com', password='p', is_active=True, role='barber'
        )
        self.barber_profile = BarberProfile.objects.create(
            user=self.barber_user, business_name='Test Barber'
        )
        self.cat = ServiceCategory.objects.create(name='Cuts')
        self.service = Service.objects.create(
            barber=self.barber_profile, category=self.cat,
            name='Haircut', price=25.00, duration_minutes=30
        )

    def test_create_booking(self):
        self.api.force_authenticate(user=self.client_user)
        r = self.api.post('/api/v1/bookings/create/', {
            'barber': self.barber_profile.id,
            'service': self.service.id,
            'date': '2026-06-01',
            'start_time': '10:00',
            'end_time': '10:30',
        }, format='json')
        self.assertEqual(r.status_code, 201)

    def test_barber_approve_booking(self):
        booking = Booking.objects.create(
            client=self.client_user, barber=self.barber_profile,
            service=self.service, date='2026-06-01',
            start_time='10:00', end_time='10:30', status='pending'
        )
        self.api.force_authenticate(user=self.barber_user)
        r = self.api.patch(f'/api/v1/bookings/business/{booking.id}/status/', {
            'status': 'approved'
        }, format='json')
        self.assertEqual(r.status_code, 200)

    def test_client_list_bookings(self):
        self.api.force_authenticate(user=self.client_user)
        r = self.api.get('/api/v1/bookings/my/')
        self.assertEqual(r.status_code, 200)


class ReviewTests(TestCase):
    def setUp(self):
        self.api = APIClient()
        self.client_user = User.objects.create_user(
            email='rv@t.com', password='p', is_active=True, role='client'
        )
        self.barber_user = User.objects.create_user(
            email='rvb@t.com', password='p', is_active=True, role='barber'
        )
        self.barber_profile = BarberProfile.objects.create(
            user=self.barber_user, business_name='Review Barber'
        )

    def test_create_review(self):
        self.api.force_authenticate(user=self.client_user)
        r = self.api.post('/api/v1/reviews/create/', {
            'barber': self.barber_profile.id, 'rating': 5, 'comment': 'Great!'
        }, format='json')
        self.assertEqual(r.status_code, 201)
        self.barber_profile.refresh_from_db()
        self.assertEqual(float(self.barber_profile.average_rating), 5.0)

    def test_public_barber_reviews(self):
        api = APIClient()
        r = api.get(f'/api/v1/reviews/barber/{self.barber_profile.id}/')
        self.assertEqual(r.status_code, 200)


class FavoriteTests(TestCase):
    def setUp(self):
        self.api = APIClient()
        self.user = User.objects.create_user(
            email='fav@t.com', password='p', is_active=True, role='client'
        )
        self.barber = User.objects.create_user(
            email='favb@t.com', password='p', is_active=True, role='barber'
        )
        self.barber_profile = BarberProfile.objects.create(
            user=self.barber, business_name='Fav Barber'
        )
        self.api.force_authenticate(user=self.user)

    def test_toggle_favorite(self):
        r = self.api.post('/api/v1/favorites/toggle/', {
            'barber_id': self.barber_profile.id
        }, format='json')
        self.assertEqual(r.status_code, 201)
        # Toggle off
        r = self.api.post('/api/v1/favorites/toggle/', {
            'barber_id': self.barber_profile.id
        }, format='json')
        self.assertEqual(r.status_code, 200)
        self.assertFalse(Favorite.objects.filter(client=self.user).exists())


class SubscriptionTests(TestCase):
    def setUp(self):
        self.api = APIClient()
        self.barber = User.objects.create_user(
            email='sub@t.com', password='p', is_active=True, role='barber'
        )
        self.plan = SubscriptionPlan.objects.create(
            name='Pro Monthly', billing_cycle='monthly', price=29.99
        )
        self.api.force_authenticate(user=self.barber)

    def test_subscribe(self):
        r = self.api.post('/api/v1/subscriptions/subscribe/', {
            'plan_id': self.plan.id
        }, format='json')
        self.assertEqual(r.status_code, 201)
        self.barber.refresh_from_db()
        self.assertTrue(self.barber.is_subscribed())

    def test_cancel_subscription(self):
        sub = Subscription.objects.create(
            user=self.barber, plan=self.plan, amount_paid=29.99
        )
        sub.activate()
        r = self.api.delete('/api/v1/subscriptions/my/')
        self.assertEqual(r.status_code, 200)
