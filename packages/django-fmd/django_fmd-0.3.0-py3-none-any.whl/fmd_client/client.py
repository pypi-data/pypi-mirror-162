import logging

import requests
from requests import Response

from fmd_client import __version__
from fmd_client.crypto import generate_hashed_password, generate_keys
from fmd_client.data_classes import ClientDeviceData, LocationData, LocationDataSize


logger = logging.getLogger(__name__)


def debug_response(response: Response, level=logging.DEBUG):
    logger.log(level, 'Response.url: %r', response.url)
    logger.log(level, 'Response.status_code: %r', response.status_code)
    logger.log(level, 'Response.headers: %r', response.headers)
    logger.log(level, 'Response.links: %r', response.links)
    logger.log(level, 'Response.content: %r', response.content)


class FmdClient:
    user_agent = f'python-fmd-client/{__version__}'

    def __init__(self, fmd_server_url, raise_wrong_responses=False, ssl_verify=True):
        logger.debug(
            'FMD server url: %r (raise_wrong_responses:%r, ssl_verify:%r)',
            fmd_server_url,
            raise_wrong_responses,
            ssl_verify,
        )
        self.fmd_server_url = fmd_server_url.rstrip('/')
        self.raise_wrong_responses = raise_wrong_responses

        self.session = requests.Session()
        self.session.verify = ssl_verify
        self.session.headers['user-agent'] = self.user_agent

    def _request(self, func, url: str, payload: dict) -> Response:
        uri = f'{self.fmd_server_url}/{url}'
        logger.debug('%s %r %r', func.__name__.upper(), uri, payload)
        response: Response = func(uri, json=payload, allow_redirects=False)

        if response.status_code > 400:
            logger.error('%s response: %r', func.__name__.upper(), response)
        else:
            logger.debug('%s response: %r', func.__name__.upper(), response)

        if response.status_code > 300:
            logger.warning('Raw response content: %r', response.content)

        response.raise_for_status()
        return response

    def put(self, url: str, payload: dict) -> Response:
        return self._request(func=self.session.put, url=url, payload=payload)

    def post(self, url: str, payload: dict) -> Response:
        return self._request(func=self.session.post, url=url, payload=payload)

    def register(self, client_device_data: ClientDeviceData):
        """
        Register a new Device
        """
        logger.debug('Register new device on %r...', self.fmd_server_url)
        assert client_device_data.hashed_password
        assert client_device_data.encrypted_private_key
        assert client_device_data.public_key_base64_str
        response = self.put(
            url='device',
            payload={
                'hashedPassword': client_device_data.hashed_password,
                'privkey': client_device_data.encrypted_private_key,
                'pubkey': client_device_data.public_key_base64_str,
            },
        )
        try:
            data = response.json()
        except Exception as err:
            logger.error('Device register error: %r', err)
            debug_response(response, level=logging.WARNING)
            raise

        device_id = data['DeviceId']
        client_device_data.short_id = device_id
        logger.info('New device registered at %r with ID: %r', self.fmd_server_url, device_id)

    def delete(self, access_token):
        """
        Delete a device
        """
        logger.debug('Delete device on %r...', self.fmd_server_url)
        response: Response = self.post(url='device', payload={'IDT': access_token})
        self._assert_empty(response)
        logger.info('Device deleted from %r', self.fmd_server_url)

    def request_access(self, client_device_data: ClientDeviceData):
        assert client_device_data.short_id
        assert client_device_data.hashed_password

        response = self.put(
            url='requestAccess',
            payload={
                'IDT': client_device_data.short_id,
                'Data': client_device_data.hashed_password,
            },
        )
        data = response.json()

        device_id = data['IDT']
        if not client_device_data.device_id:
            client_device_data.device_id = device_id
        else:
            assert device_id == client_device_data.device_id, (
                f'Device ID mismatch:'
                f' new ID {device_id!r} is not {client_device_data.device_id!r}'
            )

        access_token = data['Data']
        return access_token

    def get_key(self, access_token: str):
        response: Response = self.put(
            url='key',
            payload={
                'IDT': access_token,
                'Data': '0',  # XXX: Why?
            },
        )
        encrypted_private_key = response.text
        logger.info('Received private key (%i bytes)', len(encrypted_private_key))
        return encrypted_private_key

    def get_location_data_size(self, access_token: str, index: int = -1) -> LocationDataSize:
        response: Response = self.put(
            url='locationDataSize',
            payload={
                'IDT': access_token,
                'Data': str(index),  # FMD server accepts only a string!
            },
        )
        response_data = response.json()
        location_data_size = LocationDataSize(
            length=response_data['DataLength'],
            beginning=response_data['DataBeginningIndex'],
        )
        return location_data_size

    def get_location(self, access_token: str, index: int = -1) -> LocationData:
        response: Response = self.put(
            url='location',
            payload={
                'IDT': access_token,
                'Data': str(index),  # FMD server accepts only a string!
            },
        )
        response_data = response.json()
        location = LocationData(
            bat=response_data['Bat'],
            lat=response_data['lat'],
            lon=response_data['lon'],
            provider=response_data['Provider'],
            date=response_data['Date'],
            encrypted=True,
        )
        return location

    def send_location(self, access_token, location) -> None:
        logger.debug('Send location to %r', self.fmd_server_url)
        response: Response = self.post(
            url='location',
            payload={
                'IDT': access_token,
                'bat': location.bat,
                'lat': location.lat,
                'lon': location.lon,
                'provider': location.provider,
                'date': location.date,
            },
        )
        self._assert_empty(response)
        logger.info('Location successfully send to %r', self.fmd_server_url)

    def _assert_empty(self, response):
        if response.content != b'':
            logger.warning('Unexpected response:')
            debug_response(response, level=logging.WARNING)
            if self.raise_wrong_responses:
                raise AssertionError(f'Unexpected response: {response.content!r}')


def get_device_location(
    *, fmd_client: FmdClient, client_device_data: ClientDeviceData, index: int = -1
):
    """
    Return the device location from the FMD server
    """
    access_token = fmd_client.request_access(client_device_data)

    client_device_data.encrypted_private_key = fmd_client.get_key(access_token)

    location_data_size: LocationDataSize = fmd_client.get_location_data_size(
        access_token, index=index
    )
    logger.info(str(location_data_size))

    location = fmd_client.get_location(access_token, index=index)
    location = location.decrypt(location, client_device_data)
    return location


def send_device_location(
    *, fmd_client: FmdClient, client_device_data: ClientDeviceData, location: LocationData
) -> None:
    if not location.encrypted:
        location = location.encrypt(location, client_device_data)

    access_token = fmd_client.request_access(client_device_data)
    fmd_client.send_location(access_token, location)


def register_device(*, fmd_client: FmdClient, plaintext_password: str) -> ClientDeviceData:
    encrypted_private_key, public_key_base64_str = generate_keys(raw_password=plaintext_password)
    client_device_data = ClientDeviceData(
        plaintext_password=plaintext_password,
        hashed_password=generate_hashed_password(plaintext_password),
        encrypted_private_key=encrypted_private_key,
        public_key_base64_str=public_key_base64_str,
    )
    fmd_client.register(client_device_data)
    return client_device_data


def delete_device(*, fmd_client: FmdClient, client_device_data: ClientDeviceData) -> None:
    access_token = fmd_client.request_access(client_device_data)
    fmd_client.delete(access_token)
