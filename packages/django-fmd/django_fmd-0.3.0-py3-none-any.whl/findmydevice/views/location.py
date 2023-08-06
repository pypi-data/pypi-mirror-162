import logging
import time

from django.conf import settings
from django.http import HttpResponse, JsonResponse
from django.views import View

from findmydevice.json_utils import parse_json
from findmydevice.models import Location
from findmydevice.services.device import get_device_by_token


logger = logging.getLogger(__name__)


class LocationView(View):
    """
    /location
    """

    def post(self, request):
        """
        Store a new location from device
        """
        user_agent = request.headers.get('User-Agent')
        logger.info('Store new location, user agent: %r', user_agent)

        location_data = parse_json(request)

        bat = location_data['bat']
        raw_date = int(location_data['date'])
        lat = location_data['lat']
        lon = location_data['lon']
        provider = location_data['provider']

        access_token = location_data['IDT']
        device = get_device_by_token(token=access_token)

        time_range = int(settings.FMD_MIN_LOCATION_DATE_RANGE_SEC / 2)
        unix_now = time.time()
        min_raw_date = (unix_now - time_range) * 1000
        max_raw_date = (unix_now + time_range) * 1000
        logger.debug(
            'Skip min: %s max: %s (FMD_MIN_LOCATION_DATE_RANGE_SEC=%i)',
            min_raw_date,
            max_raw_date,
            settings.FMD_MIN_LOCATION_DATE_RANGE_SEC,
        )
        qs = Location.objects.filter(device=device)
        qs = qs.exclude(raw_date__gt=max_raw_date)
        qs = qs.exclude(raw_date__lt=min_raw_date)
        exist_count = qs.count()
        if exist_count:
            logger.warning(
                'Skip location, because we have %i in FMD_MIN_LOCATION_DATE_RANGE_SEC=%i',
                exist_count,
                settings.FMD_MIN_LOCATION_DATE_RANGE_SEC,
            )
        else:
            location = Location.objects.create(
                device=device,
                bat=bat,
                raw_date=raw_date,
                lat=lat,
                lon=lon,
                provider=provider,
                user_agent=user_agent,
            )
            logger.info('New location stored: %s', location)

        return HttpResponse(content=b'')

    def put(self, request):
        """
        Send one location back to the FMD web page
        """
        location_data = parse_json(request)
        access_token = location_data['IDT']
        index = int(location_data['Data'])
        logger.info('Location index: %r', index)

        device = get_device_by_token(token=access_token)

        queryset = Location.objects.filter(device=device).order_by('create_dt')
        count = queryset.count()
        if index >= count:
            logger.error('Location index %r is more than count: %r', index, count)
            index = count - 1

        if index == -1:
            logger.info('Use latest location (index=-1)')
            location = queryset.latest()
        else:
            location = queryset[index]

        response_data = {
            'Provider': location.provider,
            'Date': location.raw_date,
            'lon': location.lon,
            'lat': location.lat,
            'Bat': location.bat,
        }
        logger.info('PUT location (index:%r pk:%r): %r', index, location.pk, response_data)
        return JsonResponse(response_data)
