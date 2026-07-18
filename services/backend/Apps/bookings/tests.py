from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework.test import APIClient
from Apps.profiles.models import BarberProfile, SalonProfile, SalonEmployee
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


# ==============================================================================
# BARBER REGRESSION TESTS (19.1) - the barber flow must be unchanged
# ==============================================================================
class BarberRegressionTests(TestCase):
    """Guards the existing, frontend-integrated barber contract."""

    def setUp(self):
        self.api = APIClient()
        self.client_user = User.objects.create_user(
            email='regcl@t.com', password='p', is_active=True, role='client',
            full_name='Reg Client',
        )
        self.barber_user = User.objects.create_user(
            email='regbr@t.com', password='p', is_active=True, role='barber'
        )
        self.barber_profile = BarberProfile.objects.create(
            user=self.barber_user, business_name='Reg Barber'
        )
        self.cat = ServiceCategory.objects.create(name='RegCuts')
        self.service = Service.objects.create(
            barber=self.barber_profile, category=self.cat,
            name='Reg Haircut', price=25.00, duration_minutes=30,
        )
        self.date = '2026-09-01'

    def _create(self, **overrides):
        payload = {
            'barber': self.barber_profile.id,
            'service': self.service.id,
            'date': self.date,
            'start_time': '10:00',
            'end_time': '10:30',
        }
        payload.update(overrides)
        self.api.force_authenticate(user=self.client_user)
        return self.api.post('/api/v1/bookings/create/', payload, format='json')

    def test_01_barber_booking_creation_still_succeeds(self):
        r = self._create()
        self.assertEqual(r.status_code, 201)

    def test_02_legacy_payload_without_employee_remains_valid(self):
        """The exact legacy payload shape (no salon fields) still works."""
        r = self._create(notes='legacy note')
        self.assertEqual(r.status_code, 201)
        booking = Booking.objects.get(pk=r.data['data']['id'])
        self.assertEqual(booking.barber_id, self.barber_profile.id)
        self.assertIsNone(booking.salon_id)
        self.assertIsNone(booking.employee_id)

    def test_03_barber_response_structure_remains_compatible(self):
        r = self._create()
        data = r.data['data']
        # Every field the barber frontend already relies on must still be present.
        for field in (
            'id', 'client', 'client_name', 'client_email', 'barber',
            'barber_name', 'service', 'service_name', 'date', 'start_time',
            'end_time', 'status', 'notes', 'can_cancel', 'created_at',
            'updated_at', 'employee',
        ):
            self.assertIn(field, data, f"missing legacy field: {field}")
        self.assertEqual(data['barber_name'], 'Reg Barber')
        self.assertEqual(data['service_name'], 'Reg Haircut')
        self.assertEqual(data['status'], 'pending')

    def test_04_barber_booking_list_returns_barber_bookings(self):
        self._create()
        self.api.force_authenticate(user=self.barber_user)
        r = self.api.get('/api/v1/bookings/business/')
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.data['count'], 1)

    def test_05_barber_status_update_still_works(self):
        booking = Booking.objects.create(
            client=self.client_user, barber=self.barber_profile,
            service=self.service, date=self.date,
            start_time='10:00', end_time='10:30', status='pending',
        )
        self.api.force_authenticate(user=self.barber_user)
        r = self.api.patch(
            f'/api/v1/bookings/business/{booking.id}/status/',
            {'status': 'approved'}, format='json',
        )
        self.assertEqual(r.status_code, 200)
        booking.refresh_from_db()
        self.assertEqual(booking.status, 'approved')

    def test_06_barber_reschedule_still_works(self):
        booking = Booking.objects.create(
            client=self.client_user, barber=self.barber_profile,
            service=self.service, date=self.date,
            start_time='10:00', end_time='10:30', status='approved',
        )
        self.api.force_authenticate(user=self.barber_user)
        r = self.api.post(
            f'/api/v1/bookings/business/{booking.id}/reschedule/',
            {'new_date': self.date, 'new_start_time': '14:00', 'new_end_time': '14:30'},
            format='json',
        )
        self.assertEqual(r.status_code, 200)
        booking.refresh_from_db()
        self.assertEqual(booking.status, 'rescheduled')
        self.assertEqual(r.data['data']['barber'], self.barber_profile.id)

    def test_07_barber_availability_still_works(self):
        self.api.force_authenticate(user=self.barber_user)
        r = self.api.post('/api/v1/bookings/slots/', {
            'date': self.date, 'start_time': '09:00', 'end_time': '17:00',
        }, format='json')
        self.assertEqual(r.status_code, 201)

        pub = APIClient().get(f'/api/v1/bookings/availability/{self.barber_profile.id}/')
        self.assertEqual(pub.status_code, 200)
        self.assertEqual(pub.data['count'], 1)

    def test_08_barber_service_listing_still_works(self):
        r = APIClient().get(f'/api/v1/services/barber/{self.barber_profile.id}/')
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.data['count'], 1)

    def test_42_barber_completion_counter_still_works(self):
        booking = Booking.objects.create(
            client=self.client_user, barber=self.barber_profile,
            service=self.service, date=self.date,
            start_time='10:00', end_time='10:30', status='approved',
        )
        self.api.force_authenticate(user=self.barber_user)
        r = self.api.patch(
            f'/api/v1/bookings/business/{booking.id}/status/',
            {'status': 'completed'}, format='json',
        )
        self.assertEqual(r.status_code, 200)
        self.barber_profile.refresh_from_db()
        self.assertEqual(self.barber_profile.total_bookings, 1)


# ==============================================================================
# SALON TEST BASE
# ==============================================================================
class SalonTestBase(TestCase):
    """Builds two independent salons so cross-tenant isolation can be tested."""

    def setUp(self):
        self.api = APIClient()
        self.date = (timezone.now().date() + datetime.timedelta(days=7)).isoformat()
        self.past_date = (timezone.now().date() - datetime.timedelta(days=7)).isoformat()

        self.client_user = User.objects.create_user(
            email='sc@t.com', password='p', is_active=True, role='client',
            full_name='Salon Client',
        )

        # --- Salon A -------------------------------------------------------
        self.owner_a = User.objects.create_user(
            email='oa@t.com', password='p', is_active=True, role='salon',
            full_name='Owner A',
        )
        self.salon_a = SalonProfile.objects.create(
            user=self.owner_a, business_name='Salon A'
        )
        self.emp_a1 = self._make_employee(self.salon_a, 'Emp A1', 'ea1@t.com')
        self.emp_a2 = self._make_employee(self.salon_a, 'Emp A2', 'ea2@t.com')

        self.cat = ServiceCategory.objects.create(name='Colour')
        self.service_a = Service.objects.create(
            salon=self.salon_a, category=self.cat, name='Colouring',
            price=50.00, duration_minutes=30,
        )

        # --- Salon B -------------------------------------------------------
        self.owner_b = User.objects.create_user(
            email='ob@t.com', password='p', is_active=True, role='salon',
            full_name='Owner B',
        )
        self.salon_b = SalonProfile.objects.create(
            user=self.owner_b, business_name='Salon B'
        )
        self.emp_b1 = self._make_employee(self.salon_b, 'Emp B1', 'eb1@t.com')
        self.service_b = Service.objects.create(
            salon=self.salon_b, category=self.cat, name='B Cut',
            price=20.00, duration_minutes=30,
        )

        # Availability: 09:00-17:00 for A1, A2 and B1 on self.date
        for emp in (self.emp_a1, self.emp_a2, self.emp_b1):
            self._make_slot(emp, self.date)

    def _make_employee(self, salon, full_name, email):
        user = User.objects.create_user(
            email=email, password='p', full_name=full_name, role='salon',
            is_active=True, is_verified=True, is_sub_profile=True,
            parent_salon=salon.user,
        )
        return SalonEmployee.objects.create(
            salon=salon, user=user,
            generated_email=email, generated_password='Ab1@2345',
        )

    def _make_slot(self, employee, date, start='09:00', end='17:00'):
        return TimeSlot.objects.create(
            salon=employee.salon, employee=employee, date=date,
            start_time=start, end_time=end,
        )

    def _booking_payload(self, **overrides):
        payload = {
            'salon': self.salon_a.id,
            'employee': self.emp_a1.id,
            'service': self.service_a.id,
            'date': self.date,
            'start_time': '10:00',
            'end_time': '10:30',
        }
        payload.update(overrides)
        return payload

    def _create_salon_booking(self, **overrides):
        self.api.force_authenticate(user=self.client_user)
        return self.api.post(
            '/api/v1/bookings/salon/create/', self._booking_payload(**overrides),
            format='json',
        )

    def _make_booking(self, employee=None, status='pending', start='11:00', end='11:30'):
        employee = employee or self.emp_a1
        return Booking.objects.create(
            client=self.client_user, barber=None, salon=employee.salon,
            employee=employee, service=(
                self.service_a if employee.salon_id == self.salon_a.id else self.service_b
            ),
            date=self.date, start_time=start, end_time=end, status=status,
        )


# ==============================================================================
# SALON BOOKING CREATION TESTS (19.2)
# ==============================================================================
class SalonBookingCreateTests(SalonTestBase):

    def test_09_client_can_create_salon_booking(self):
        r = self._create_salon_booking()
        self.assertEqual(r.status_code, 201, r.data)
        self.assertEqual(
            r.data['message'],
            'Booking created successfully and is awaiting confirmation.',
        )

    def test_10_salon_booking_stores_salon_and_employee(self):
        r = self._create_salon_booking()
        booking = Booking.objects.get(pk=r.data['data']['id'])
        self.assertEqual(booking.salon_id, self.salon_a.id)
        self.assertEqual(booking.employee_id, self.emp_a1.id)
        self.assertEqual(booking.client_id, self.client_user.id)
        self.assertEqual(booking.status, 'pending')

    def test_11_salon_booking_requires_no_barber(self):
        r = self._create_salon_booking()
        booking = Booking.objects.get(pk=r.data['data']['id'])
        self.assertIsNone(booking.barber_id)
        self.assertIsNone(r.data['data']['barber'])
        self.assertIsNone(r.data['data']['barber_name'])
        self.assertEqual(r.data['data']['booking_type'], 'salon')
        self.assertEqual(r.data['data']['salon_name'], 'Salon A')
        self.assertEqual(r.data['data']['employee_name'], 'Emp A1')

    def test_12_cannot_create_without_employee(self):
        self.api.force_authenticate(user=self.client_user)
        payload = self._booking_payload()
        payload.pop('employee')
        r = self.api.post('/api/v1/bookings/salon/create/', payload, format='json')
        self.assertEqual(r.status_code, 400)
        self.assertIn('employee', r.data['errors'])

    def test_13_cannot_select_employee_from_another_salon(self):
        r = self._create_salon_booking(employee=self.emp_b1.id)
        self.assertEqual(r.status_code, 400)
        self.assertIn('employee', r.data['errors'])
        self.assertEqual(Booking.objects.count(), 0)

    def test_14_cannot_select_service_from_another_salon(self):
        r = self._create_salon_booking(service=self.service_b.id)
        self.assertEqual(r.status_code, 400)
        self.assertIn('service', r.data['errors'])
        self.assertEqual(Booking.objects.count(), 0)

    def test_15_cannot_select_inactive_employee(self):
        self.emp_a1.is_active = False
        self.emp_a1.save(update_fields=['is_active'])
        r = self._create_salon_booking()
        self.assertEqual(r.status_code, 400)
        self.assertIn('employee', r.data['errors'])

    def test_16_cannot_select_inactive_service(self):
        self.service_a.is_active = False
        self.service_a.save(update_fields=['is_active'])
        r = self._create_salon_booking()
        self.assertEqual(r.status_code, 400)
        self.assertIn('service', r.data['errors'])

    def test_17_cannot_book_outside_employee_availability(self):
        # Availability is 09:00-17:00; 18:00 is outside it.
        r = self._create_salon_booking(start_time='18:00', end_time='18:30')
        self.assertEqual(r.status_code, 400)
        self.assertIn('start_time', r.data['errors'])

    def test_18_cannot_double_book_same_employee(self):
        self._make_booking(employee=self.emp_a1, start='10:00', end='10:30')
        r = self._create_salon_booking(start_time='10:15', end_time='10:45')
        self.assertEqual(r.status_code, 400)

    def test_19_different_employees_can_be_booked_at_same_time(self):
        r1 = self._create_salon_booking(employee=self.emp_a1.id)
        self.assertEqual(r1.status_code, 201)
        r2 = self._create_salon_booking(employee=self.emp_a2.id)
        self.assertEqual(r2.status_code, 201, r2.data)

    def test_20_past_bookings_are_rejected(self):
        self._make_slot(self.emp_a1, self.past_date)
        r = self._create_salon_booking(date=self.past_date)
        self.assertEqual(r.status_code, 400)
        self.assertIn('date', r.data['errors'])

    def test_client_cannot_spoof_another_client(self):
        other = User.objects.create_user(
            email='other@t.com', password='p', is_active=True, role='client'
        )
        r = self._create_salon_booking(client=other.id)
        self.assertEqual(r.status_code, 201)
        booking = Booking.objects.get(pk=r.data['data']['id'])
        # `client` is ignored and taken from the authenticated user.
        self.assertEqual(booking.client_id, self.client_user.id)

    def test_duration_must_match_service(self):
        r = self._create_salon_booking(start_time='10:00', end_time='11:00')
        self.assertEqual(r.status_code, 400)
        self.assertIn('end_time', r.data['errors'])

    def test_employee_not_eligible_for_restricted_service(self):
        self.service_a.available_employees.add(self.emp_a2)
        r = self._create_salon_booking(employee=self.emp_a1.id)
        self.assertEqual(r.status_code, 400)
        self.assertIn('service', r.data['errors'])

    def test_employee_eligible_when_listed(self):
        self.service_a.available_employees.add(self.emp_a1)
        r = self._create_salon_booking(employee=self.emp_a1.id)
        self.assertEqual(r.status_code, 201, r.data)

    def test_non_client_cannot_create_salon_booking(self):
        self.api.force_authenticate(user=self.owner_a)
        r = self.api.post(
            '/api/v1/bookings/salon/create/', self._booking_payload(), format='json'
        )
        self.assertEqual(r.status_code, 403)

    def test_salon_not_accepting_clients_is_rejected(self):
        self.salon_a.is_accepting_clients = False
        self.salon_a.save(update_fields=['is_accepting_clients'])
        r = self._create_salon_booking()
        self.assertEqual(r.status_code, 400)
        self.assertIn('salon', r.data['errors'])


# ==============================================================================
# EMPLOYEE VISIBILITY TESTS (19.3)
# ==============================================================================
class SalonEmployeeVisibilityTests(SalonTestBase):

    def test_21_employee_sees_only_assigned_bookings(self):
        mine = self._make_booking(employee=self.emp_a1, start='11:00', end='11:30')
        self._make_booking(employee=self.emp_a2, start='12:00', end='12:30')
        self.api.force_authenticate(user=self.emp_a1.user)
        r = self.api.get('/api/v1/bookings/salon/employee/bookings/')
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.data['count'], 1)
        self.assertEqual(r.data['results'][0]['id'], mine.id)

    def test_22_employee_cannot_list_another_employees_bookings(self):
        self._make_booking(employee=self.emp_a2, start='12:00', end='12:30')
        self.api.force_authenticate(user=self.emp_a1.user)
        r = self.api.get('/api/v1/bookings/salon/employee/bookings/')
        self.assertEqual(r.data['count'], 0)

    def test_23_employee_cannot_retrieve_another_employees_booking_by_id(self):
        other = self._make_booking(employee=self.emp_a2, start='12:00', end='12:30')
        self.api.force_authenticate(user=self.emp_a1.user)
        r = self.api.get(f'/api/v1/bookings/salon/employee/bookings/{other.id}/')
        self.assertEqual(r.status_code, 404)

    def test_24_employee_cannot_update_another_employees_booking(self):
        other = self._make_booking(employee=self.emp_a2, start='12:00', end='12:30')
        self.api.force_authenticate(user=self.emp_a1.user)
        r = self.api.patch(
            f'/api/v1/bookings/salon/business/{other.id}/status/',
            {'status': 'approved'}, format='json',
        )
        self.assertEqual(r.status_code, 404)
        other.refresh_from_db()
        self.assertEqual(other.status, 'pending')

    def test_25_employee_can_update_assigned_booking(self):
        mine = self._make_booking(employee=self.emp_a1)
        self.api.force_authenticate(user=self.emp_a1.user)
        r = self.api.patch(
            f'/api/v1/bookings/salon/business/{mine.id}/status/',
            {'status': 'approved'}, format='json',
        )
        self.assertEqual(r.status_code, 200)
        mine.refresh_from_db()
        self.assertEqual(mine.status, 'approved')

    def test_invalid_transition_rejected(self):
        mine = self._make_booking(employee=self.emp_a1, status='pending')
        self.api.force_authenticate(user=self.emp_a1.user)
        r = self.api.patch(
            f'/api/v1/bookings/salon/business/{mine.id}/status/',
            {'status': 'completed'}, format='json',
        )
        self.assertEqual(r.status_code, 400)

    def test_employee_from_other_salon_cannot_touch_booking(self):
        mine = self._make_booking(employee=self.emp_a1)
        self.api.force_authenticate(user=self.emp_b1.user)
        r = self.api.get(f'/api/v1/bookings/salon/employee/bookings/{mine.id}/')
        self.assertEqual(r.status_code, 404)


# ==============================================================================
# SALON OWNER VISIBILITY TESTS (19.4)
# ==============================================================================
class SalonOwnerVisibilityTests(SalonTestBase):

    def test_26_owner_sees_all_salon_bookings(self):
        self._make_booking(employee=self.emp_a1, start='11:00', end='11:30')
        self._make_booking(employee=self.emp_a2, start='12:00', end='12:30')
        self._make_booking(employee=self.emp_b1, start='13:00', end='13:30')
        self.api.force_authenticate(user=self.owner_a)
        r = self.api.get('/api/v1/bookings/salon/owner/bookings/')
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.data['count'], 2)

    def test_27_owner_can_filter_by_employee(self):
        b1 = self._make_booking(employee=self.emp_a1, start='11:00', end='11:30')
        self._make_booking(employee=self.emp_a2, start='12:00', end='12:30')
        self.api.force_authenticate(user=self.owner_a)
        r = self.api.get(f'/api/v1/bookings/salon/owner/bookings/?employee={self.emp_a1.id}')
        self.assertEqual(r.data['count'], 1)
        self.assertEqual(r.data['results'][0]['id'], b1.id)

    def test_28_owner_can_filter_by_status(self):
        self._make_booking(employee=self.emp_a1, status='approved', start='11:00', end='11:30')
        self._make_booking(employee=self.emp_a2, status='pending', start='12:00', end='12:30')
        self.api.force_authenticate(user=self.owner_a)
        r = self.api.get('/api/v1/bookings/salon/owner/bookings/?status=approved')
        self.assertEqual(r.data['count'], 1)

    def test_29_owner_can_filter_by_date_and_range(self):
        self._make_booking(employee=self.emp_a1, start='11:00', end='11:30')
        self.api.force_authenticate(user=self.owner_a)

        r = self.api.get(f'/api/v1/bookings/salon/owner/bookings/?date={self.date}')
        self.assertEqual(r.data['count'], 1)

        r = self.api.get(f'/api/v1/bookings/salon/owner/bookings/?date_from={self.date}&date_to={self.date}')
        self.assertEqual(r.data['count'], 1)

        far = (timezone.now().date() + datetime.timedelta(days=90)).isoformat()
        r = self.api.get(f'/api/v1/bookings/salon/owner/bookings/?date_from={far}')
        self.assertEqual(r.data['count'], 0)

    def test_30_owner_cannot_see_another_salons_bookings(self):
        self._make_booking(employee=self.emp_b1, start='13:00', end='13:30')
        self.api.force_authenticate(user=self.owner_a)
        r = self.api.get('/api/v1/bookings/salon/owner/bookings/')
        self.assertEqual(r.data['count'], 0)

    def test_31_owner_cannot_retrieve_another_salons_booking_by_id(self):
        foreign = self._make_booking(employee=self.emp_b1, start='13:00', end='13:30')
        self.api.force_authenticate(user=self.owner_a)
        r = self.api.get(f'/api/v1/bookings/salon/owner/bookings/{foreign.id}/')
        self.assertEqual(r.status_code, 404)

    def test_32_owner_cannot_update_another_salons_booking(self):
        foreign = self._make_booking(employee=self.emp_b1, start='13:00', end='13:30')
        self.api.force_authenticate(user=self.owner_a)
        r = self.api.patch(
            f'/api/v1/bookings/salon/business/{foreign.id}/status/',
            {'status': 'approved'}, format='json',
        )
        self.assertEqual(r.status_code, 404)
        foreign.refresh_from_db()
        self.assertEqual(foreign.status, 'pending')

    def test_owner_can_update_own_salon_booking(self):
        booking = self._make_booking(employee=self.emp_a1)
        self.api.force_authenticate(user=self.owner_a)
        r = self.api.patch(
            f'/api/v1/bookings/salon/business/{booking.id}/status/',
            {'status': 'approved'}, format='json',
        )
        self.assertEqual(r.status_code, 200)

    def test_client_cannot_access_owner_endpoint(self):
        self.api.force_authenticate(user=self.client_user)
        r = self.api.get('/api/v1/bookings/salon/owner/bookings/')
        self.assertEqual(r.status_code, 403)

    def test_employee_cannot_access_owner_endpoint(self):
        self.api.force_authenticate(user=self.emp_a1.user)
        r = self.api.get('/api/v1/bookings/salon/owner/bookings/')
        self.assertEqual(r.status_code, 403)


# ==============================================================================
# SERVICE AND AVAILABILITY TESTS (19.5)
# ==============================================================================
class SalonServiceAndAvailabilityTests(SalonTestBase):

    def test_33_owner_can_manage_only_own_salon_services(self):
        self.api.force_authenticate(user=self.owner_a)

        r = self.api.get('/api/v1/services/salon/manage/')
        self.assertEqual(r.status_code, 200)
        self.assertEqual(len(r.data['data']), 1)
        self.assertEqual(r.data['data'][0]['id'], self.service_a.id)

        # Salon B's service is invisible and unreachable.
        r = self.api.get(f'/api/v1/services/salon/manage/{self.service_b.id}/')
        self.assertEqual(r.status_code, 404)

        r = self.api.patch(
            f'/api/v1/services/salon/manage/{self.service_b.id}/',
            {'price': '1.00'}, format='json',
        )
        self.assertEqual(r.status_code, 404)
        self.service_b.refresh_from_db()
        self.assertEqual(float(self.service_b.price), 20.00)

    def test_owner_can_create_salon_service(self):
        self.api.force_authenticate(user=self.owner_a)
        r = self.api.post('/api/v1/services/salon/manage/', {
            'name': 'Blow Dry', 'price': '15.00', 'duration_minutes': 20,
            'category': self.cat.id,
        }, format='json')
        self.assertEqual(r.status_code, 201, r.data)
        service = Service.objects.get(pk=r.data['data']['id'])
        self.assertEqual(service.salon_id, self.salon_a.id)
        self.assertIsNone(service.barber_id)

    def test_owner_cannot_assign_foreign_employee_to_service(self):
        self.api.force_authenticate(user=self.owner_a)
        r = self.api.post('/api/v1/services/salon/manage/', {
            'name': 'Restricted', 'price': '15.00', 'duration_minutes': 20,
            'available_employees': [self.emp_b1.id],
        }, format='json')
        self.assertEqual(r.status_code, 400)

    def test_employee_cannot_manage_salon_services(self):
        self.api.force_authenticate(user=self.emp_a1.user)
        r = self.api.get('/api/v1/services/salon/manage/')
        self.assertEqual(r.status_code, 403)

    def test_34_public_salon_services_returns_only_active(self):
        Service.objects.create(
            salon=self.salon_a, name='Hidden', price=5.00,
            duration_minutes=10, is_active=False,
        )
        r = APIClient().get(f'/api/v1/services/salon/{self.salon_a.id}/')
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.data['count'], 1)
        self.assertEqual(r.data['results'][0]['name'], 'Colouring')

    def test_public_salon_services_excludes_barber_services(self):
        r = APIClient().get(f'/api/v1/services/salon/{self.salon_a.id}/')
        names = [s['name'] for s in r.data['results']]
        self.assertNotIn('Reg Haircut', names)

    def test_35_public_availability_returns_only_that_employee(self):
        r = APIClient().get(f'/api/v1/bookings/salon/availability/{self.emp_a1.id}/')
        self.assertEqual(r.status_code, 200)
        self.assertEqual(len(r.data['data']), 1)
        self.assertEqual(r.data['data'][0]['employee'], self.emp_a1.id)

    def test_public_availability_excludes_booked_windows(self):
        # The single 09:00-17:00 slot overlaps this booking, so it disappears.
        self._make_booking(employee=self.emp_a1, start='10:00', end='10:30')
        r = APIClient().get(f'/api/v1/bookings/salon/availability/{self.emp_a1.id}/')
        self.assertEqual(len(r.data['data']), 0)

    def test_public_availability_404_for_inactive_employee(self):
        self.emp_a1.is_active = False
        self.emp_a1.save(update_fields=['is_active'])
        r = APIClient().get(f'/api/v1/bookings/salon/availability/{self.emp_a1.id}/')
        self.assertEqual(r.status_code, 404)

    def test_public_availability_exposes_no_credentials(self):
        r = APIClient().get(f'/api/v1/bookings/salon/availability/{self.emp_a1.id}/')
        body = str(r.data)
        self.assertNotIn('generated_password', body)
        self.assertNotIn('Ab1@2345', body)

    def test_36_employee_can_manage_only_own_slots(self):
        self.api.force_authenticate(user=self.emp_a1.user)

        r = self.api.get('/api/v1/bookings/salon/employee/slots/')
        self.assertEqual(r.status_code, 200)
        self.assertEqual(len(r.data['data']), 1)

        r = self.api.post('/api/v1/bookings/salon/employee/slots/', {
            'date': self.date, 'start_time': '18:00', 'end_time': '19:00',
        }, format='json')
        self.assertEqual(r.status_code, 201, r.data)
        slot = TimeSlot.objects.get(pk=r.data['data']['id'])
        self.assertEqual(slot.employee_id, self.emp_a1.id)
        self.assertEqual(slot.salon_id, self.salon_a.id)
        self.assertIsNone(slot.barber_id)

        # Another employee's slot is not reachable.
        foreign = TimeSlot.objects.filter(employee=self.emp_a2).first()
        r = self.api.patch(
            f'/api/v1/bookings/salon/employee/slots/{foreign.id}/',
            {'is_blocked': True}, format='json',
        )
        self.assertEqual(r.status_code, 404)

    def test_employee_can_delete_own_slot(self):
        slot = TimeSlot.objects.get(employee=self.emp_a1)
        self.api.force_authenticate(user=self.emp_a1.user)
        r = self.api.delete(f'/api/v1/bookings/salon/employee/slots/{slot.id}/')
        self.assertEqual(r.status_code, 200)
        self.assertFalse(TimeSlot.objects.filter(pk=slot.id).exists())

    def test_37_owner_cannot_manage_another_salons_slots(self):
        foreign = TimeSlot.objects.get(employee=self.emp_b1)
        self.api.force_authenticate(user=self.owner_a)

        r = self.api.patch(
            f'/api/v1/bookings/salon/owner/slots/{foreign.id}/',
            {'is_blocked': True}, format='json',
        )
        self.assertEqual(r.status_code, 404)

        r = self.api.delete(f'/api/v1/bookings/salon/owner/slots/{foreign.id}/')
        self.assertEqual(r.status_code, 404)
        self.assertTrue(TimeSlot.objects.filter(pk=foreign.id).exists())

        # And cannot create a slot for a foreign employee.
        r = self.api.post('/api/v1/bookings/salon/owner/slots/', {
            'employee': self.emp_b1.id, 'date': self.date,
            'start_time': '20:00', 'end_time': '21:00',
        }, format='json')
        self.assertEqual(r.status_code, 404)

    def test_owner_can_manage_own_salon_slots(self):
        self.api.force_authenticate(user=self.owner_a)
        r = self.api.get('/api/v1/bookings/salon/owner/slots/')
        self.assertEqual(r.status_code, 200)
        self.assertEqual(len(r.data['data']), 2)  # emp_a1 + emp_a2

        r = self.api.post('/api/v1/bookings/salon/owner/slots/', {
            'employee': self.emp_a1.id, 'date': self.date,
            'start_time': '20:00', 'end_time': '21:00',
        }, format='json')
        self.assertEqual(r.status_code, 201, r.data)


# ==============================================================================
# COMPLETION AND RESCHEDULING TESTS (19.6)
# ==============================================================================
class SalonCompletionAndRescheduleTests(SalonTestBase):

    def test_38_completing_increments_employee_total_bookings(self):
        booking = self._make_booking(employee=self.emp_a1, status='approved')
        self.api.force_authenticate(user=self.owner_a)
        r = self.api.patch(
            f'/api/v1/bookings/salon/business/{booking.id}/status/',
            {'status': 'completed'}, format='json',
        )
        self.assertEqual(r.status_code, 200)
        self.emp_a1.refresh_from_db()
        self.assertEqual(self.emp_a1.total_bookings, 1)

    def test_39_completing_does_not_touch_null_barber(self):
        booking = self._make_booking(employee=self.emp_a1, status='approved')
        self.assertIsNone(booking.barber_id)
        self.api.force_authenticate(user=self.emp_a1.user)
        # Would raise AttributeError if the counter dereferenced booking.barber.
        r = self.api.patch(
            f'/api/v1/bookings/salon/business/{booking.id}/status/',
            {'status': 'completed'}, format='json',
        )
        self.assertEqual(r.status_code, 200)
        booking.refresh_from_db()
        self.assertEqual(booking.status, 'completed')
        self.assertIsNone(booking.barber_id)

    def test_40_reschedule_preserves_salon_employee_service_client(self):
        booking = self._make_booking(employee=self.emp_a1, status='approved')
        self.api.force_authenticate(user=self.owner_a)
        r = self.api.post(
            f'/api/v1/bookings/salon/business/{booking.id}/reschedule/',
            {'new_date': self.date, 'new_start_time': '14:00', 'new_end_time': '14:30'},
            format='json',
        )
        self.assertEqual(r.status_code, 200, r.data)

        booking.refresh_from_db()
        self.assertEqual(booking.status, 'rescheduled')

        new_booking = Booking.objects.get(pk=r.data['data']['id'])
        self.assertEqual(new_booking.salon_id, self.salon_a.id)
        self.assertEqual(new_booking.employee_id, self.emp_a1.id)
        self.assertEqual(new_booking.service_id, self.service_a.id)
        self.assertEqual(new_booking.client_id, self.client_user.id)
        self.assertEqual(new_booking.rescheduled_from_id, booking.id)
        self.assertIsNone(new_booking.barber_id)
        self.assertEqual(new_booking.status, 'approved')

    def test_41_reschedule_rejects_employee_conflicts(self):
        booking = self._make_booking(employee=self.emp_a1, status='approved', start='11:00', end='11:30')
        self._make_booking(employee=self.emp_a1, status='approved', start='14:00', end='14:30')
        self.api.force_authenticate(user=self.owner_a)
        r = self.api.post(
            f'/api/v1/bookings/salon/business/{booking.id}/reschedule/',
            {'new_date': self.date, 'new_start_time': '14:15', 'new_end_time': '14:45'},
            format='json',
        )
        self.assertEqual(r.status_code, 400)
        booking.refresh_from_db()
        self.assertEqual(booking.status, 'approved')

    def test_reschedule_rejects_outside_availability(self):
        booking = self._make_booking(employee=self.emp_a1, status='approved')
        self.api.force_authenticate(user=self.owner_a)
        r = self.api.post(
            f'/api/v1/bookings/salon/business/{booking.id}/reschedule/',
            {'new_date': self.date, 'new_start_time': '22:00', 'new_end_time': '22:30'},
            format='json',
        )
        self.assertEqual(r.status_code, 400)

    def test_employee_cannot_reschedule_another_employees_booking(self):
        booking = self._make_booking(employee=self.emp_a2, status='approved')
        self.api.force_authenticate(user=self.emp_a1.user)
        r = self.api.post(
            f'/api/v1/bookings/salon/business/{booking.id}/reschedule/',
            {'new_date': self.date, 'new_start_time': '14:00', 'new_end_time': '14:30'},
            format='json',
        )
        self.assertEqual(r.status_code, 404)


# ==============================================================================
# CLIENT VISIBILITY ACROSS BOTH BOOKING TYPES (section 9)
# ==============================================================================
class ClientMixedBookingVisibilityTests(SalonTestBase):

    def test_client_list_includes_both_types_without_error(self):
        barber_user = User.objects.create_user(
            email='mixbr@t.com', password='p', is_active=True, role='barber'
        )
        barber_profile = BarberProfile.objects.create(
            user=barber_user, business_name='Mixed Barber'
        )
        Booking.objects.create(
            client=self.client_user, barber=barber_profile, date=self.date,
            start_time='09:00', end_time='09:30', status='pending',
        )
        self._make_booking(employee=self.emp_a1)

        self.api.force_authenticate(user=self.client_user)
        r = self.api.get('/api/v1/bookings/my/')
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.data['count'], 2)

        by_type = {b['booking_type']: b for b in r.data['results']}
        self.assertIsNone(by_type['salon']['barber_name'])
        self.assertEqual(by_type['salon']['salon_name'], 'Salon A')
        self.assertEqual(by_type['barber']['barber_name'], 'Mixed Barber')
        self.assertIsNone(by_type['barber']['salon_name'])

    def test_client_cannot_see_other_clients_bookings(self):
        self._make_booking(employee=self.emp_a1)
        other = User.objects.create_user(
            email='nosy@t.com', password='p', is_active=True, role='client'
        )
        self.api.force_authenticate(user=other)
        r = self.api.get('/api/v1/bookings/my/')
        self.assertEqual(r.data['count'], 0)


# ==============================================================================
# MODEL-LEVEL INTEGRITY (section 4.1)
# ==============================================================================
class BookingModelValidationTests(SalonTestBase):

    def test_rejects_booking_with_neither_business(self):
        from django.core.exceptions import ValidationError
        b = Booking(client=self.client_user, date=self.date,
                    start_time='10:00', end_time='10:30')
        with self.assertRaises(ValidationError):
            b.clean()

    def test_rejects_booking_with_both_businesses(self):
        from django.core.exceptions import ValidationError
        barber_user = User.objects.create_user(
            email='both@t.com', password='p', is_active=True, role='barber'
        )
        barber_profile = BarberProfile.objects.create(
            user=barber_user, business_name='Both'
        )
        b = Booking(client=self.client_user, barber=barber_profile,
                    salon=self.salon_a, employee=self.emp_a1, date=self.date,
                    start_time='10:00', end_time='10:30')
        with self.assertRaises(ValidationError):
            b.clean()

    def test_rejects_salon_booking_without_employee(self):
        from django.core.exceptions import ValidationError
        b = Booking(client=self.client_user, salon=self.salon_a, date=self.date,
                    start_time='10:00', end_time='10:30')
        with self.assertRaises(ValidationError):
            b.clean()

    def test_rejects_employee_from_another_salon(self):
        from django.core.exceptions import ValidationError
        b = Booking(client=self.client_user, salon=self.salon_a,
                    employee=self.emp_b1, date=self.date,
                    start_time='10:00', end_time='10:30')
        with self.assertRaises(ValidationError):
            b.clean()

    def test_db_constraint_blocks_two_businesses(self):
        from django.db import IntegrityError
        barber_user = User.objects.create_user(
            email='dbc@t.com', password='p', is_active=True, role='barber'
        )
        barber_profile = BarberProfile.objects.create(
            user=barber_user, business_name='DBC'
        )
        with self.assertRaises(IntegrityError):
            Booking.objects.create(
                client=self.client_user, barber=barber_profile,
                salon=self.salon_a, employee=self.emp_a1, date=self.date,
                start_time='10:00', end_time='10:30',
            )

    def test_db_constraint_blocks_salon_booking_without_employee(self):
        from django.db import IntegrityError
        with self.assertRaises(IntegrityError):
            Booking.objects.create(
                client=self.client_user, salon=self.salon_a, date=self.date,
                start_time='10:00', end_time='10:30',
            )

    def test_barber_booking_endpoint_rejects_salon_employee(self):
        barber_user = User.objects.create_user(
            email='rej@t.com', password='p', is_active=True, role='barber'
        )
        barber_profile = BarberProfile.objects.create(
            user=barber_user, business_name='Rej'
        )
        self.api.force_authenticate(user=self.client_user)
        r = self.api.post('/api/v1/bookings/create/', {
            'barber': barber_profile.id, 'employee': self.emp_a1.id,
            'date': self.date, 'start_time': '10:00', 'end_time': '10:30',
        }, format='json')
        self.assertEqual(r.status_code, 400)
        self.assertIn('employee', r.data['errors'])


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
        self.admin = User.objects.create_user(
            email='sub-admin@t.com', password='p', is_active=True, role='admin'
        )
        self.plan = SubscriptionPlan.objects.create(
            name='Pro Monthly', billing_cycle='monthly', price=29.99
        )
        self.api.force_authenticate(user=self.barber)

    def test_barber_cannot_self_subscribe_manually(self):
        # /subscribe/ is admin/internal-only now (see PAYMENT_SYSTEM_CURRENT_FLOW_ANALYSIS.md
        # / Apps.subscriptions security fix) — real self-service purchases go
        # through Stripe Checkout instead.
        r = self.api.post('/api/v1/subscriptions/subscribe/', {
            'plan_id': self.plan.id
        }, format='json')
        self.assertEqual(r.status_code, 403)

    def test_admin_can_manually_subscribe_a_barber(self):
        self.api.force_authenticate(user=self.admin)
        r = self.api.post('/api/v1/subscriptions/subscribe/', {
            'plan_id': self.plan.id, 'user_id': self.barber.id,
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
