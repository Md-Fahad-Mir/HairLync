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

    # Employee management
    path('employees/', views.EmployeeListCreateView.as_view(), name='employee-list-create'),
    path('employees/<int:pk>/', views.EmployeeDetailView.as_view(), name='employee-detail'),
]
