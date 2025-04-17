from django.contrib import admin
from django.urls import path, include
from django.conf import settings


api_v1_patterns = [
    path('auth/', include("dj_rest_auth.urls")),
    path('auth/registration/', include("dj_rest_auth.registration.urls")),
    path('auth/google/', include("allauth.socialaccount.urls")),
    path("auth-app/", include(("auth_app.urls", "auth_app"), namespace="auth_app")),
    path('courses/', include(('courses.urls', 'courses'), namespace='courses')),
]

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/', include(api_v1_patterns)),
]

if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [
        path('__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns