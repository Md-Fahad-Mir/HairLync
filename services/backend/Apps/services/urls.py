from django.urls import path
from . import views

app_name = 'services'

urlpatterns = [
    path('categories/', views.ServiceCategoryListView.as_view(), name='category-list'),
    path('categories/create/', views.ServiceCategoryAdminView.as_view(), name='category-create'),
    path('my/', views.BarberServiceListCreateView.as_view(), name='barber-services'),
    path('my/<int:pk>/', views.BarberServiceDetailView.as_view(), name='barber-service-detail'),
    path('barber/<int:barber_id>/', views.BarberServicesPublicView.as_view(), name='barber-services-public'),
]
