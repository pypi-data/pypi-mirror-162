from django.conf import settings
from django.conf.urls import include, static
from django.contrib import admin
from django.urls import path

from findmydevice.admin.fmd_admin_site import fmd_admin_site


admin.autodiscover()

urlpatterns = [  # Don't use i18n_patterns() here
    path('admin/', fmd_admin_site.urls),
    path('', include('findmydevice.urls')),
]


if settings.SERVE_FILES:
    urlpatterns += static.static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)


if settings.DEBUG:
    import debug_toolbar

    urlpatterns = [
        path('__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns
