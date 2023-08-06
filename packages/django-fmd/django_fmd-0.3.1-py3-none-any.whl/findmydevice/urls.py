from django.conf import settings
from django.urls import path
from django.views.static import serve

import findmydevice
from findmydevice.views.base_views import PictureView
from findmydevice.views.command import CommandView
from findmydevice.views.device import DeviceView
from findmydevice.views.key import KeyView
from findmydevice.views.location import LocationView
from findmydevice.views.location_data_size import LocationDataSizeView
from findmydevice.views.push import PushView
from findmydevice.views.request_access import RequestAccessView
from findmydevice.views.version import VersionView
from findmydevice.views.web_page import FmdWebPageView


urlpatterns = [
    path('command', CommandView.as_view(), name='command'),
    path('location', LocationView.as_view(), name='location'),
    path('locationDataSize', LocationDataSizeView.as_view(), name='location_data_size'),
    path('picture', PictureView.as_view(), name='picture'),
    path('key', KeyView.as_view(), name='key'),
    path('device', DeviceView.as_view(), name='device'),
    path('push', PushView.as_view(), name='push'),
    path('requestAccess', RequestAccessView.as_view(), name='request_access'),
    path('version', VersionView.as_view(), name='version'),
    path('', FmdWebPageView.as_view(), name='fmd-web-page'),
]
if settings.DEBUG:
    # TODO: Serve from real Web server ;)
    urlpatterns.append(path('<path:path>', serve, {'document_root': findmydevice.WEB_PATH}))
