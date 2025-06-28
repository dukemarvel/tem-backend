from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView



api_v1_patterns = [
    path('auth/login/',  TokenObtainPairView.as_view(),      name='token_obtain_pair'),
    path('auth/token/refresh/', TokenRefreshView.as_view(),  name='token_refresh'),
    path('auth/', include("dj_rest_auth.urls")),
    path('auth/registration/', include("dj_rest_auth.registration.urls")),
    path('auth/google/', include("allauth.socialaccount.urls")),
    path('courses/', include(('courses.urls', 'courses'), namespace='courses')),
    path("scorm/", include(("scorm_player.urls", "scorm"), namespace="scorm")),
    path("progress/", include(("progress.urls"), namespace="progress")),
    path("payments/", include(("payments.urls","payments"), namespace="payments")),
    path("notifications/", include("notifications.urls", namespace="notifications")),
    path('teams/', include(('teams.urls', 'teams'), namespace='teams')),
]

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/', include(api_v1_patterns)),
]

if settings.DEBUG:
    import debug_toolbar
    # put the debug toolbar at the very front
    urlpatterns.insert(0, path('__debug__/', include(debug_toolbar.urls)))
    # serve media files too
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)