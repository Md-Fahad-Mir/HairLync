from django.urls import path
from . import views

app_name = 'subscriptions'

urlpatterns = [
    path('plans/', views.SubscriptionPlanListView.as_view(), name='plan-list'),
    path('plans/create/', views.SubscriptionPlanAdminView.as_view(), name='plan-create'),
    path('subscribe/', views.SubscriptionCreateView.as_view(), name='subscribe'),
    path('my/', views.SubscriptionDetailView.as_view(), name='subscription-detail'),
    path('history/', views.SubscriptionHistoryView.as_view(), name='subscription-history'),
]
