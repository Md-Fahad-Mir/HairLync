from django.urls import path
from . import views

app_name = 'favorites'

urlpatterns = [
    path('', views.FavoriteListView.as_view(), name='favorite-list'),
    path('toggle/', views.FavoriteToggleView.as_view(), name='favorite-toggle'),
]
