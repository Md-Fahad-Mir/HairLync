from django.urls import path
from . import views

app_name = 'bookings'

urlpatterns = [
    # Client bookings
    path('create/', views.ClientBookingCreateView.as_view(), name='booking-create'),
    path('my/', views.ClientBookingListView.as_view(), name='client-bookings'),
    path('my/<int:pk>/', views.ClientBookingDetailView.as_view(), name='client-booking-detail'),

    # Barber bookings
    path('business/', views.BarberBookingListView.as_view(), name='barber-bookings'),
    path('business/<int:pk>/status/', views.BarberBookingStatusView.as_view(), name='booking-status-update'),
    path('business/<int:pk>/reschedule/', views.BarberBookingRescheduleView.as_view(), name='booking-reschedule'),

    # Availability
    path('slots/', views.TimeSlotListCreateView.as_view(), name='time-slots'),
    path('availability/<int:barber_id>/', views.PublicAvailabilityView.as_view(), name='public-availability'),

    # ---------------------------------------------------------------------
    # Salon booking flow (additive - the barber routes above are untouched)
    # ---------------------------------------------------------------------
    # Client
    path('salon/create/', views.SalonBookingCreateView.as_view(), name='salon-booking-create'),

    # Public employee availability
    path(
        'salon/availability/<int:employee_id>/',
        views.SalonEmployeeAvailabilityView.as_view(),
        name='salon-public-availability',
    ),

    # Employee: own availability
    path('salon/employee/slots/', views.SalonEmployeeSlotListCreateView.as_view(), name='salon-employee-slots'),
    path('salon/employee/slots/<int:pk>/', views.SalonEmployeeSlotDetailView.as_view(), name='salon-employee-slot-detail'),

    # Employee: assigned bookings
    path('salon/employee/bookings/', views.SalonEmployeeBookingListView.as_view(), name='salon-employee-bookings'),
    path('salon/employee/bookings/<int:pk>/', views.SalonEmployeeBookingDetailView.as_view(), name='salon-employee-booking-detail'),

    # Owner: salon-wide availability
    path('salon/owner/slots/', views.SalonOwnerSlotListCreateView.as_view(), name='salon-owner-slots'),
    path('salon/owner/slots/<int:pk>/', views.SalonOwnerSlotDetailView.as_view(), name='salon-owner-slot-detail'),

    # Owner: salon-wide bookings
    path('salon/owner/bookings/', views.SalonOwnerBookingListView.as_view(), name='salon-owner-bookings'),
    path('salon/owner/bookings/<int:pk>/', views.SalonOwnerBookingDetailView.as_view(), name='salon-owner-booking-detail'),

    # Owner or assigned employee: manage a salon booking
    path('salon/business/<int:pk>/status/', views.SalonBookingStatusView.as_view(), name='salon-booking-status'),
    path('salon/business/<int:pk>/reschedule/', views.SalonBookingRescheduleView.as_view(), name='salon-booking-reschedule'),
]
