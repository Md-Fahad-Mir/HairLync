from django.urls import path
from . import views

app_name = 'education'

urlpatterns = [
    path('categories/', views.EducationCategoryListView.as_view(), name='category-list'),
    path('content/', views.EducationalContentListView.as_view(), name='content-list'),
    path('content/create/', views.EducationalContentAdminView.as_view(), name='content-create'),
    path('content/<slug:slug>/', views.EducationalContentDetailView.as_view(), name='content-detail'),
]
