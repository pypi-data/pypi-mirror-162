import logging

import requests
from django.http import JsonResponse
from django.views import View

from findmydevice.json_utils import parse_json
from findmydevice.services.device import get_device_by_token


logger = logging.getLogger(__name__)


class PushView(View):
    def put(self, request):
        """
        Register push services from the FMD app.
        """
        user_agent = request.headers.get('User-Agent')
        logger.info('Register push services, user agent: %r', user_agent)

        app_data = parse_json(request)

        device_token = app_data['IDT']
        device = get_device_by_token(token=device_token)

        push_url = app_data['Data']
        if not push_url:
            logger.error('No push URL send!')
        elif push_url == device.push_url:
            logger.info('Push URL %r already stored for %s', push_url, device)
        else:
            logger.info('Store new push URL: %r for %s', push_url, device)
            response = requests.get(push_url)
            response.raise_for_status()
            response_data = response.json()
            logger.info('Push URL response: %r', response_data)
            device.push_url = push_url
            if user_agent:
                device.user_agent = user_agent
            device.full_clean()
            device.save()
            device.push_notification(text='Registered FMD services successful 😀')

        response_data = {
            # TODO
        }
        return JsonResponse(response_data)
