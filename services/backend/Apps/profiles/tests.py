from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from Apps.profiles.models import BarberProfile, ClientProfile, SalonProfile, SalonEmployee

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


class SalonProfileTests(TestCase):
    def setUp(self):
        self.api = APIClient()
        self.user = User.objects.create_user(
            email='salon@t.com', password='p', is_active=True, role='salon'
        )
        self.api.force_authenticate(user=self.user)

    def test_create_salon_profile(self):
        r = self.api.post('/api/v1/profiles/salon/', {
            'business_name': 'The Sky Lounge', 'city': 'NYC',
        }, format='json')
        self.assertEqual(r.status_code, 200)
        self.assertTrue(SalonProfile.objects.filter(user=self.user).exists())

    def test_salon_search_public(self):
        api = APIClient()
        r = api.get('/api/v1/profiles/salons/search/')
        self.assertEqual(r.status_code, 200)


class SalonEmployeeTests(TestCase):
    def setUp(self):
        self.api = APIClient()
        self.salon_user = User.objects.create_user(
            email='salonowner@t.com', password='p', is_active=True, role='salon'
        )
        self.salon_profile = SalonProfile.objects.create(
            user=self.salon_user, business_name='The Sky Lounge'
        )
        self.api.force_authenticate(user=self.salon_user)

    def test_add_employee(self):
        r = self.api.post('/api/v1/profiles/salon/employees/', {
            'full_name': 'John Smith',
        }, format='json')
        self.assertEqual(r.status_code, 201)
        # Verify auto-generated credentials
        employee = SalonEmployee.objects.first()
        self.assertIn('@hairlync.app', employee.generated_email)
        self.assertEqual(len(employee.generated_password), 8)

    def test_list_employees(self):
        r = self.api.get('/api/v1/profiles/salon/employees/')
        self.assertEqual(r.status_code, 200)

    def test_employee_login_and_self_profile(self):
        # Create an employee
        r = self.api.post('/api/v1/profiles/salon/employees/', {
            'full_name': 'Jane Doe',
        }, format='json')
        self.assertEqual(r.status_code, 201)

        employee = SalonEmployee.objects.first()

        # Login as the employee
        emp_api = APIClient()
        login_r = emp_api.post('/api/v1/auth/login/', {
            'email': employee.generated_email,
            'password': employee.generated_password,
        }, format='json')
        self.assertEqual(login_r.status_code, 200)

    def test_sub_profile_cannot_create_employees(self):
        # Create an employee first
        self.api.post('/api/v1/profiles/salon/employees/', {
            'full_name': 'Jane Doe',
        }, format='json')
        employee = SalonEmployee.objects.first()

        # Login as the employee and try to create another employee
        emp_api = APIClient()
        emp_api.force_authenticate(user=employee.user)
        r = emp_api.post('/api/v1/profiles/salon/employees/', {
            'full_name': 'Another Employee',
        }, format='json')
        # Should be denied (403) - sub-profile cannot create employees
        self.assertEqual(r.status_code, 403)
