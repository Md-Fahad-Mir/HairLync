from django.urls import path
from . import views

app_name = 'profiles'

urlpatterns = [
    # Client profile
    path('client/', views.ClientProfileView.as_view(), name='client-profile'),

    # Barber profile (own)
    path('barber/', views.BarberProfileView.as_view(), name='barber-profile'),

    # Barber public
    path('barber/<int:pk>/', views.BarberProfileDetailView.as_view(), name='barber-detail'),
    path('barbers/search/', views.BarberSearchView.as_view(), name='barber-search'),

    # Salon profile (own)
    path('salon/', views.SalonProfileView.as_view(), name='salon-profile'),

    # Salon public
    path('salon/<int:pk>/', views.SalonProfileDetailView.as_view(), name='salon-detail'),
    path('salons/search/', views.SalonSearchView.as_view(), name='salon-search'),

    # Salon employee management (salon owner only)
    path('salon/employees/', views.SalonEmployeeListCreateView.as_view(), name='salon-employee-list-create'),
    path('salon/employees/<int:pk>/', views.SalonEmployeeDetailView.as_view(), name='salon-employee-detail'),

    # Salon employee self-profile (sub-profile user)
    path('employee/me/', views.SalonEmployeeSelfProfileView.as_view(), name='salon-employee-self'),
]
