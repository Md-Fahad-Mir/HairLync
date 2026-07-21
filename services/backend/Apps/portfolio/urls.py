from django.urls import path
from . import views

app_name = 'portfolio'

urlpatterns = [
    # Barber portfolio (backward compatible)
    path('barber/', views.BarberPortfolioListCreateView.as_view(), name='portfolio-list-create'),
    path('barber/<int:pk>/', views.PortfolioDetailView.as_view(), name='portfolio-detail'),

    # Salon portfolio
    path('salon/my/', views.SalonPortfolioListCreateView.as_view(), name='salon-portfolio-list-create'),
    path('salon/my/<int:pk>/', views.PortfolioDetailView.as_view(), name='salon-portfolio-detail'),

    # Salon employee portfolio
    path('employee/my/', views.SalonEmployeePortfolioListCreateView.as_view(), name='employee-portfolio-list-create'),
    path('employee/my/<int:pk>/', views.PortfolioDetailView.as_view(), name='employee-portfolio-detail'),

    # Public views
    path('barber/<int:barber_id>/', views.BarberPortfolioPublicView.as_view(), name='barber-portfolio-public'),
]
