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
]
