from django.urls import path
from . import views

app_name = 'portfolio'

urlpatterns = [
    path('my/', views.PortfolioListCreateView.as_view(), name='portfolio-list-create'),
    path('my/<int:pk>/', views.PortfolioDetailView.as_view(), name='portfolio-detail'),
    path('barber/<int:barber_id>/', views.BarberPortfolioPublicView.as_view(), name='barber-portfolio-public'),
]
