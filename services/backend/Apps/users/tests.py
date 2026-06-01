from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from Apps.users.models import PendingUser, ForgotPasswordRequest

User = get_user_model()


class UserModelTests(TestCase):
    def test_create_user(self):
        user = User.objects.create_user(email='test@test.com', password='testpass123')
        self.assertEqual(user.email, 'test@test.com')
        self.assertFalse(user.is_active)
        self.assertEqual(user.role, 'client')

    def test_create_superuser(self):
        user = User.objects.create_superuser(email='admin@test.com', password='adminpass123')
        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_active)
        self.assertEqual(user.role, 'admin')

    def test_user_roles(self):
        client = User.objects.create_user(email='c@t.com', password='p', role='client')
        barber = User.objects.create_user(email='b@t.com', password='p', role='barber')
        self.assertTrue(client.is_client)
        self.assertFalse(client.is_barber)
        self.assertTrue(barber.is_barber)
        self.assertFalse(barber.is_client)

    def test_subscription_check(self):
        user = User.objects.create_user(email='s@t.com', password='p')
        self.assertFalse(user.is_subscribed())
        user.paid_user = True
        user.current_plan = 'monthly'
        user.save()
        self.assertTrue(user.is_subscribed())


class RegisterAPITests(TestCase):
    def setUp(self):
        self.client_api = APIClient()

    def test_register_client(self):
        data = {
            'email': 'newclient@test.com',
            'full_name': 'New Client',
            'password': 'StrongPass123!',
            'confirm_password': 'StrongPass123!',
            'role': 'client',
        }
        response = self.client_api.post('/api/v1/auth/register/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(PendingUser.objects.filter(email='newclient@test.com').exists())

    def test_register_duplicate_email(self):
        User.objects.create_user(email='dup@test.com', password='pass')
        data = {
            'email': 'dup@test.com',
            'full_name': 'Dup',
            'password': 'StrongPass123!',
            'confirm_password': 'StrongPass123!',
            'role': 'client',
        }
        response = self.client_api.post('/api/v1/auth/register/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_password_mismatch(self):
        data = {
            'email': 'mm@test.com',
            'full_name': 'MM',
            'password': 'StrongPass123!',
            'confirm_password': 'DifferentPass123!',
            'role': 'client',
        }
        response = self.client_api.post('/api/v1/auth/register/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class OTPVerificationTests(TestCase):
    def setUp(self):
        self.client_api = APIClient()

    def test_verify_otp_success(self):
        pending = PendingUser.objects.create(
            email='otp@test.com', full_name='OTP User',
            password='hashed_password', role='client'
        )
        otp = pending.generate_otp()
        response = self.client_api.post('/api/v1/auth/verify-otp/', {
            'email': 'otp@test.com', 'otp': otp
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(User.objects.filter(email='otp@test.com').exists())

    def test_verify_otp_invalid(self):
        pending = PendingUser.objects.create(
            email='otp2@test.com', full_name='OTP2',
            password='hashed', role='client'
        )
        pending.generate_otp()
        response = self.client_api.post('/api/v1/auth/verify-otp/', {
            'email': 'otp2@test.com', 'otp': '000000'
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class LoginLogoutTests(TestCase):
    def setUp(self):
        self.client_api = APIClient()
        self.user = User.objects.create_user(
            email='login@test.com', password='StrongPass123!',
            is_active=True, role='client'
        )

    def test_login_success(self):
        response = self.client_api.post('/api/v1/auth/login/', {
            'email': 'login@test.com', 'password': 'StrongPass123!'
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
        self.assertEqual(response.data['user']['role'], 'client')

    def test_login_wrong_password(self):
        response = self.client_api.post('/api/v1/auth/login/', {
            'email': 'login@test.com', 'password': 'WrongPass!'
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_logout(self):
        login = self.client_api.post('/api/v1/auth/login/', {
            'email': 'login@test.com', 'password': 'StrongPass123!'
        }, format='json')
        self.client_api.credentials(HTTP_AUTHORIZATION=f"Bearer {login.data['access']}")
        response = self.client_api.post('/api/v1/auth/logout/', {
            'refresh': login.data['refresh']
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class PasswordTests(TestCase):
    def setUp(self):
        self.client_api = APIClient()
        self.user = User.objects.create_user(
            email='pwd@test.com', password='OldPass123!',
            is_active=True, role='client'
        )

    def test_change_password(self):
        self.client_api.force_authenticate(user=self.user)
        response = self.client_api.post('/api/v1/auth/change-password/', {
            'old_password': 'OldPass123!',
            'new_password': 'NewPass123!',
            'confirm_password': 'NewPass123!',
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_forgot_password(self):
        response = self.client_api.post('/api/v1/auth/forgot-password/', {
            'email': 'pwd@test.com'
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(ForgotPasswordRequest.objects.filter(email='pwd@test.com').exists())


class UserMeTests(TestCase):
    def setUp(self):
        self.client_api = APIClient()
        self.user = User.objects.create_user(
            email='me@test.com', password='Pass123!',
            is_active=True, full_name='Me User', role='client'
        )
        self.client_api.force_authenticate(user=self.user)

    def test_get_me(self):
        response = self.client_api.get('/api/v1/auth/me/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['data']['email'], 'me@test.com')

    def test_update_me(self):
        response = self.client_api.patch('/api/v1/auth/me/', {
            'full_name': 'Updated Name'
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertEqual(self.user.full_name, 'Updated Name')


class PermissionTests(TestCase):
    def setUp(self):
        self.client_api = APIClient()
        self.client_user = User.objects.create_user(
            email='client@test.com', password='p', is_active=True, role='client'
        )
        self.barber_user = User.objects.create_user(
            email='barber@test.com', password='p', is_active=True, role='barber'
        )

    def test_client_cannot_access_barber_endpoints(self):
        self.client_api.force_authenticate(user=self.client_user)
        response = self.client_api.get('/api/v1/profiles/barber/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_barber_cannot_access_client_endpoints(self):
        self.client_api.force_authenticate(user=self.barber_user)
        response = self.client_api.get('/api/v1/profiles/client/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_unauthenticated_cannot_access_protected(self):
        response = self.client_api.get('/api/v1/auth/me/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
