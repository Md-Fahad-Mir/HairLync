from django.urls import path
from . import views

app_name = 'recommendations'

urlpatterns = [
    path('categories/', views.HairStyleCategoryListView.as_view(), name='category-list'),
    path('upload-image/', views.ClientImageUploadView.as_view(), name='upload-image'),
    path('create/', views.StyleRecommendationCreateView.as_view(), name='recommendation-create'),
    path('received/', views.ClientRecommendationsView.as_view(), name='client-recommendations'),
    path('created/', views.BarberRecommendationsView.as_view(), name='barber-recommendations'),
]
