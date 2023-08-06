from django.test import LiveServerTestCase, override_settings

from findmydevice.models import Device, Location
from findmydevice_project.tests.fixtures import get_fixtures, get_json_fixtures
from fmd_client.client import (
    FmdClient,
    delete_device,
    get_device_location,
    register_device,
    send_device_location,
)
from fmd_client.data_classes import ClientDeviceData, LocationData


@override_settings(SECURE_SSL_REDIRECT=False)
class FmdClientTest(LiveServerTestCase):
    def _get_fmd_client(self):
        fmd_client = FmdClient(
            fmd_server_url=self.live_server_url,
            raise_wrong_responses=True,
            ssl_verify=False,
        )
        return fmd_client

    def test_get_location_data(self):
        hashed_password = (
            '06760f52af81bfe8f9406a65fda7f7b16484e91c55beaa36e5a1209985ffb0ee'  # "foo"
        )
        device = Device.objects.create(
            name='Test Device 1',
            hashed_password=hashed_password,
            privkey=get_fixtures('device1/private_key'),
            pubkey=get_fixtures('device1/public_key'),
        )
        device.full_clean()

        encrypted_location_data = get_json_fixtures('device1/location1.json')
        location = Location.objects.create(
            device=device,
            bat=encrypted_location_data['bat'],
            lat=encrypted_location_data['lat'],
            lon=encrypted_location_data['lon'],
            provider=encrypted_location_data['provider'],
            raw_date=12346567890,
        )
        location.full_clean()

        client_device_data = ClientDeviceData(
            short_id=device.short_id,
            plaintext_password='foo',
            hashed_password=hashed_password,
        )
        last_location = get_device_location(
            fmd_client=self._get_fmd_client(),
            client_device_data=client_device_data,
        )
        assert last_location == LocationData(
            bat='66',
            lat='52.516265',
            lon='13.37738',
            provider='network',
            date=12346567890,
            encrypted=False,
        )

    def test_register_device(self):
        assert Device.objects.count() == 0

        client_device_data = register_device(
            fmd_client=self._get_fmd_client(),
            plaintext_password='foo',
        )
        assert isinstance(client_device_data, ClientDeviceData)
        short_id = client_device_data.short_id
        assert short_id

        device = Device.objects.first()
        assert short_id == device.short_id
        hashed_password = '06760f52af81bfe8f9406a65fda7f7b16484e91c55beaa36e5a1209985ffb0ee'
        assert device.hashed_password == hashed_password

    def test_send_location(self):
        encrypted_private_key = get_fixtures('device1/private_key')
        public_key_base64_str = get_fixtures('device1/public_key')
        hashed_password = (
            '06760f52af81bfe8f9406a65fda7f7b16484e91c55beaa36e5a1209985ffb0ee'  # "foo"
        )

        device = Device.objects.create(
            name='Test Device 1',
            hashed_password=hashed_password,
            privkey=encrypted_private_key,
            pubkey=public_key_base64_str,
        )
        device.full_clean()

        client_device_data = ClientDeviceData(
            short_id=device.short_id,
            plaintext_password='foo',
            hashed_password=hashed_password,
            encrypted_private_key=encrypted_private_key,
            public_key_base64_str=public_key_base64_str,
        )

        plain_location = LocationData(
            bat='66',
            lat='52.516265',
            lon='13.37738',
            provider='network',
            date=12346567890,
            encrypted=False,
        )

        assert Location.objects.count() == 0
        send_device_location(
            fmd_client=self._get_fmd_client(),
            client_device_data=client_device_data,
            location=plain_location,
        )
        assert Location.objects.count() == 1
        location = Location.objects.first()
        encrypted_location = LocationData(
            bat=location.bat,
            lat=location.lat,
            lon=location.lon,
            provider=location.provider,
            date=location.raw_date,
            encrypted=True,
        )
        decrypted_location = LocationData.decrypt(encrypted_location, client_device_data)
        assert decrypted_location == plain_location

    def test_delete_device(self):
        hashed_password = (
            '06760f52af81bfe8f9406a65fda7f7b16484e91c55beaa36e5a1209985ffb0ee'  # "foo"
        )
        device = Device.objects.create(
            name='Test Device 1',
            hashed_password=hashed_password,
            # privkey=get_fixtures('device1/private_key'),
            # pubkey=get_fixtures('device1/public_key'),
        )
        device.full_clean()

        client_device_data = ClientDeviceData(
            short_id=device.short_id,
            plaintext_password='foo',
            hashed_password=hashed_password,
        )
        assert Device.objects.count() == 1
        delete_device(fmd_client=self._get_fmd_client(), client_device_data=client_device_data)
        assert Device.objects.count() == 0
