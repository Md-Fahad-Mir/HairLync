from django.urls import path
from . import views

app_name = 'reviews'

urlpatterns = [
    path('create/', views.ReviewCreateView.as_view(), name='review-create'),
    path('barber/<int:barber_id>/', views.BarberReviewListView.as_view(), name='barber-reviews'),
    path('<int:pk>/respond/', views.BarberReviewResponseView.as_view(), name='review-respond'),
    path('<int:pk>/moderate/', views.ReviewModerationView.as_view(), name='review-moderate'),
]
