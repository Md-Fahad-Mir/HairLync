from django.contrib import admin
from django.urls import path, include

from django.shortcuts import redirect
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from django.conf import settings
from django.conf.urls.static import static

#=====================================================================
# Schema View Configuration
#=====================================================================
schema_view = get_schema_view(
    openapi.Info(
        title="HairIQ API",
        default_version='v1',
        description="""
        ## HairIQ REST API
        
        Intelligent hair analysis & recommendation platform connecting clients 
        with professional barbers and hairdressers.
        
        ### Features
        - Dual-role authentication (Client / Barber)
        - JWT-based security with token refresh & blacklisting
        - Barber search by location, category, rating
        - Appointment booking with real-time availability
        - Portfolio & service management
        - Reviews & ratings with moderation
        - Subscription-based access for professionals
        - AI recommendation preparation support
        - Educational content with premium gating
        
        **Backend Engineer:** Md Fahad Mir  
        **Version:** v1 Stable  
        **Access:** Private
        """,
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

#=====================================================================
# Redirect to Docs Settings
#=====================================================================  
def redirect_to_docs(request):
    """Redirect root URL to API documentation"""
    return redirect('schema-swagger-ui')


urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Swagger / API docs
    path('api/docs/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('api/redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    path('api/swagger.json', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('api/docs/swagger.yaml', schema_view.without_ui(cache_timeout=0), name='schema-yaml'),
    
    # App URLs
    path('api/v1/auth/', include('Apps.users.urls', namespace='users')),
    path('api/v1/profiles/', include('Apps.profiles.urls', namespace='profiles')),
    path('api/v1/services/', include('Apps.services.urls', namespace='services')),
    path('api/v1/bookings/', include('Apps.bookings.urls', namespace='bookings')),
    path('api/v1/reviews/', include('Apps.reviews.urls', namespace='reviews')),
    path('api/v1/favorites/', include('Apps.favorites.urls', namespace='favorites')),
    path('api/v1/subscriptions/', include('Apps.subscriptions.urls', namespace='subscriptions')),
    path('api/v1/portfolio/', include('Apps.portfolio.urls', namespace='portfolio')),
    path('api/v1/recommendations/', include('Apps.recommendations.urls', namespace='recommendations')),
    path('api/v1/education/', include('Apps.education.urls', namespace='education')),
    
    # Root redirect
    path('', redirect_to_docs, name='root-redirect'),
]

#=====================================================================
# Static & Media Files (Development)
#=====================================================================
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
