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


# ==============================================================================
# NEARBY BARBER TESTS
# ==============================================================================
class NearbyBarberTests(TestCase):
    """
    Tests for GET /api/v1/profiles/barbers/nearby/

    Reference coordinates (London area):
      Client  : 51.500000, -0.120000  (near Westminster)
      Near    : 51.505000, -0.115000  (~0.7 km away)  - should appear
      Far     : 51.600000,  0.200000  (~24 km away)   - should be excluded
    """

    CLIENT_LAT = '51.500000'
    CLIENT_LON = '-0.120000'
    NEAR_LAT   = '51.505000'
    NEAR_LON   = '-0.115000'
    FAR_LAT    = '51.600000'
    FAR_LON    = '0.200000'

    def setUp(self):
        self.api = APIClient()

        # Client user + profile with saved location
        self.client_user = User.objects.create_user(
            email='nearby_client@t.com', password='pass', is_active=True, role='client'
        )
        self.client_profile = ClientProfile.objects.create(
            user=self.client_user,
            latitude=self.CLIENT_LAT,
            longitude=self.CLIENT_LON,
        )
        self.api.force_authenticate(user=self.client_user)

        # Barber user near the client
        self.barber_user_near = User.objects.create_user(
            email='barber_near@t.com', password='pass', is_active=True, role='barber'
        )
        self.barber_near = BarberProfile.objects.create(
            user=self.barber_user_near,
            business_name='Near Cuts',
            latitude=self.NEAR_LAT,
            longitude=self.NEAR_LON,
        )

        # Barber user far from the client (> 10 km)
        self.barber_user_far = User.objects.create_user(
            email='barber_far@t.com', password='pass', is_active=True, role='barber'
        )
        self.barber_far = BarberProfile.objects.create(
            user=self.barber_user_far,
            business_name='Far Cuts',
            latitude=self.FAR_LAT,
            longitude=self.FAR_LON,
        )

        # Barber with NULL coordinates
        self.barber_user_null = User.objects.create_user(
            email='barber_null@t.com', password='pass', is_active=True, role='barber'
        )
        self.barber_null = BarberProfile.objects.create(
            user=self.barber_user_null,
            business_name='No Location Cuts',
            latitude=None,
            longitude=None,
        )

    # ------------------------------------------------------------------
    def test_nearby_returns_200(self):
        r = self.api.get('/api/v1/profiles/barbers/nearby/')
        self.assertEqual(r.status_code, 200)

    def test_nearby_barber_is_included(self):
        """The barber ~0.7 km away must appear in results."""
        r = self.api.get('/api/v1/profiles/barbers/nearby/')
        self.assertEqual(r.status_code, 200)
        ids = [b['id'] for b in r.data['results']]
        self.assertIn(self.barber_near.id, ids)

    def test_far_barber_is_excluded(self):
        """The barber ~24 km away must NOT appear in results."""
        r = self.api.get('/api/v1/profiles/barbers/nearby/')
        self.assertEqual(r.status_code, 200)
        ids = [b['id'] for b in r.data['results']]
        self.assertNotIn(self.barber_far.id, ids)

    def test_null_coordinate_barber_is_excluded(self):
        """Barbers with NULL coordinates must be excluded."""
        r = self.api.get('/api/v1/profiles/barbers/nearby/')
        self.assertEqual(r.status_code, 200)
        ids = [b['id'] for b in r.data['results']]
        self.assertNotIn(self.barber_null.id, ids)

    def test_distance_km_present_and_rounded(self):
        """Each result must include distance_km rounded to 2 decimal places."""
        r = self.api.get('/api/v1/profiles/barbers/nearby/')
        self.assertEqual(r.status_code, 200)
        for barber in r.data['results']:
            self.assertIn('distance_km', barber)
            dist = barber['distance_km']
            self.assertIsNotNone(dist)
            # Verify it's rounded to at most 2 decimal places
            self.assertEqual(dist, round(dist, 2))

    def test_results_ordered_nearest_first(self):
        """Add a second near barber and verify ascending distance order."""
        barber_user_medium = User.objects.create_user(
            email='barber_medium@t.com', password='pass',
            is_active=True, role='barber'
        )
        BarberProfile.objects.create(
            user=barber_user_medium,
            business_name='Medium Cuts',
            latitude='51.502000',   # ~0.25 km from client
            longitude='-0.118000',
        )
        r = self.api.get('/api/v1/profiles/barbers/nearby/')
        self.assertEqual(r.status_code, 200)
        distances = [b['distance_km'] for b in r.data['results']]
        self.assertEqual(distances, sorted(distances))

    def test_unauthenticated_returns_401(self):
        anon = APIClient()
        r = anon.get('/api/v1/profiles/barbers/nearby/')
        self.assertEqual(r.status_code, 401)

    def test_no_client_profile_returns_empty(self):
        """Client with no saved profile gets an empty list (not an error)."""
        new_user = User.objects.create_user(
            email='noclientprofile@t.com', password='pass',
            is_active=True, role='client'
        )
        api2 = APIClient()
        api2.force_authenticate(user=new_user)
        r = api2.get('/api/v1/profiles/barbers/nearby/')
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.data['results'], [])

    def test_client_no_lat_lon_returns_empty(self):
        """Client profile without lat/lon saved returns empty list."""
        new_user = User.objects.create_user(
            email='noloc@t.com', password='pass', is_active=True, role='client'
        )
        ClientProfile.objects.create(user=new_user)  # no lat/lon
        api2 = APIClient()
        api2.force_authenticate(user=new_user)
        r = api2.get('/api/v1/profiles/barbers/nearby/')
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.data['results'], [])

    def test_existing_filters_preserved(self):
        """Filtering by category still works alongside the nearby logic."""
        self.barber_near.category = 'stylist'
        self.barber_near.save()
        r = self.api.get('/api/v1/profiles/barbers/nearby/?category=barber')
        self.assertEqual(r.status_code, 200)
        for barber in r.data['results']:
            self.assertEqual(barber['category'], 'barber')


# ==============================================================================
# NEARBY SALON TESTS
# ==============================================================================
class NearbySalonTests(TestCase):
    """
    Tests for GET /api/v1/profiles/salons/nearby/
    Same coordinate logic as NearbyBarberTests.
    """

    CLIENT_LAT = '51.500000'
    CLIENT_LON = '-0.120000'
    NEAR_LAT   = '51.505000'
    NEAR_LON   = '-0.115000'
    FAR_LAT    = '51.600000'
    FAR_LON    = '0.200000'

    def setUp(self):
        self.api = APIClient()

        self.client_user = User.objects.create_user(
            email='salon_client@t.com', password='pass', is_active=True, role='client'
        )
        self.client_profile = ClientProfile.objects.create(
            user=self.client_user,
            latitude=self.CLIENT_LAT,
            longitude=self.CLIENT_LON,
        )
        self.api.force_authenticate(user=self.client_user)

        self.salon_user_near = User.objects.create_user(
            email='salon_near@t.com', password='pass', is_active=True, role='salon'
        )
        self.salon_near = SalonProfile.objects.create(
            user=self.salon_user_near,
            business_name='Near Salon',
            latitude=self.NEAR_LAT,
            longitude=self.NEAR_LON,
        )

        self.salon_user_far = User.objects.create_user(
            email='salon_far@t.com', password='pass', is_active=True, role='salon'
        )
        self.salon_far = SalonProfile.objects.create(
            user=self.salon_user_far,
            business_name='Far Salon',
            latitude=self.FAR_LAT,
            longitude=self.FAR_LON,
        )

        self.salon_user_null = User.objects.create_user(
            email='salon_null@t.com', password='pass', is_active=True, role='salon'
        )
        self.salon_null = SalonProfile.objects.create(
            user=self.salon_user_null,
            business_name='No Location Salon',
            latitude=None,
            longitude=None,
        )

    # ------------------------------------------------------------------
    def test_nearby_salon_is_included(self):
        r = self.api.get('/api/v1/profiles/salons/nearby/')
        self.assertEqual(r.status_code, 200)
        ids = [s['id'] for s in r.data['results']]
        self.assertIn(self.salon_near.id, ids)

    def test_far_salon_is_excluded(self):
        r = self.api.get('/api/v1/profiles/salons/nearby/')
        self.assertEqual(r.status_code, 200)
        ids = [s['id'] for s in r.data['results']]
        self.assertNotIn(self.salon_far.id, ids)

    def test_null_coordinate_salon_is_excluded(self):
        r = self.api.get('/api/v1/profiles/salons/nearby/')
        self.assertEqual(r.status_code, 200)
        ids = [s['id'] for s in r.data['results']]
        self.assertNotIn(self.salon_null.id, ids)

    def test_distance_km_present(self):
        r = self.api.get('/api/v1/profiles/salons/nearby/')
        self.assertEqual(r.status_code, 200)
        for salon in r.data['results']:
            self.assertIn('distance_km', salon)
            self.assertIsNotNone(salon['distance_km'])

    def test_unauthenticated_returns_401(self):
        anon = APIClient()
        r = anon.get('/api/v1/profiles/salons/nearby/')
        self.assertEqual(r.status_code, 401)
