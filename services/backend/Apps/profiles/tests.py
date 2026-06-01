from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from Apps.profiles.models import BarberProfile, ClientProfile, EmployeeProfile

User = get_user_model()


class ClientProfileTests(TestCase):
    def setUp(self):
        self.api = APIClient()
        self.user = User.objects.create_user(
            email='c@t.com', password='p', is_active=True, role='client'
        )
        self.api.force_authenticate(user=self.user)

    def test_get_client_profile(self):
        r = self.api.get('/api/v1/profiles/client/')
        self.assertEqual(r.status_code, 200)

    def test_update_client_profile(self):
        r = self.api.patch('/api/v1/profiles/client/', {'city': 'NYC'}, format='json')
        self.assertEqual(r.status_code, 200)


class BarberProfileTests(TestCase):
    def setUp(self):
        self.api = APIClient()
        self.user = User.objects.create_user(
            email='b@t.com', password='p', is_active=True, role='barber'
        )
        self.api.force_authenticate(user=self.user)

    def test_create_barber_profile(self):
        r = self.api.post('/api/v1/profiles/barber/', {
            'business_name': 'Test Shop', 'city': 'LA', 'category': 'barber'
        }, format='json')
        self.assertEqual(r.status_code, 200)
        self.assertTrue(BarberProfile.objects.filter(user=self.user).exists())

    def test_barber_search_public(self):
        api = APIClient()
        r = api.get('/api/v1/profiles/barbers/search/')
        self.assertEqual(r.status_code, 200)


class EmployeeTests(TestCase):
    def setUp(self):
        self.api = APIClient()
        self.barber = User.objects.create_user(
            email='boss@t.com', password='p', is_active=True, role='barber'
        )
        self.profile = BarberProfile.objects.create(
            user=self.barber, business_name='Boss Shop'
        )
        self.api.force_authenticate(user=self.barber)

    def test_add_employee(self):
        r = self.api.post('/api/v1/profiles/employees/', {
            'email': 'emp@t.com', 'full_name': 'Emp', 'password': 'EmpPass123!'
        }, format='json')
        self.assertEqual(r.status_code, 201)

    def test_list_employees(self):
        r = self.api.get('/api/v1/profiles/employees/')
        self.assertEqual(r.status_code, 200)
