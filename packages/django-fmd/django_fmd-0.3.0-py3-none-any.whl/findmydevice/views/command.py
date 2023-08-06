import logging

import requests
from django.http import JsonResponse
from django.views import View

from findmydevice.json_utils import parse_json
from findmydevice.models import Device
from findmydevice.services.device import get_device_by_token


logger = logging.getLogger(__name__)


class CommandView(View):
    def post(self, request):
        """
        Store a new command from the Web Page
        """
        app_data = parse_json(request)
        command = app_data['Data']
        device_token = app_data['IDT']
        device: Device = get_device_by_token(token=device_token)

        device.command2user = command
        device.full_clean()
        device.save()

        push_url = device.push_url
        if not push_url:
            logger.error('Device %s has not push URL!', device)
        else:
            response = requests.post(
                push_url,  # XXX: /up=1 -> /message ?!?
                json={
                    'message': 'magic may begin',
                    'priority': 5,
                },
            )
            response.raise_for_status()
            response_data = response.json()
            logger.info('Push response: %r', response_data)

        response_data = {
            # TODO
        }
        return JsonResponse(response_data)

    def put(self, request):
        """
        Send current command back to zhe FMD app
        """
        app_data = parse_json(request)

        device_token = app_data['IDT']
        device: Device = get_device_by_token(token=device_token)

        response_data = {'IDT': device_token, 'Data': device.command2user}
        logger.info('Send Command back: %r', response_data)
        return JsonResponse(response_data)
