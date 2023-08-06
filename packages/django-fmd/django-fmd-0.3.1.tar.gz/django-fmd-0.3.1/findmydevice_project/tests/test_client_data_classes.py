import dataclasses

from django.test import SimpleTestCase

from findmydevice_project.tests.fixtures import get_fixtures
from fmd_client.data_classes import ClientDeviceData, LocationData


class ClientDataClassesTestCase(SimpleTestCase):
    def test_location(self):
        client_device_data = ClientDeviceData(
            plaintext_password='foo',
            hashed_password='06760f52af81bfe8f9406a65fda7f7b16484e91c55beaa36e5a1209985ffb0ee',
            encrypted_private_key=get_fixtures('device1/private_key'),
            public_key_base64_str=get_fixtures('device1/public_key'),
        )

        plain_location = LocationData(
            bat='66',
            lat='52.516265',
            lon='13.37738',
            provider='network',
            date=12346567890,
            encrypted=False,
        )

        encrypted_location = LocationData.encrypt(plain_location, client_device_data)
        assert encrypted_location.encrypted is True

        encrypted_keys = set()
        for key, value in dataclasses.asdict(encrypted_location).items():
            if key in ('date', 'encrypted'):
                continue
            assert isinstance(value, str)
            assert len(value) > 16
            encrypted_keys.add(key)
        assert encrypted_keys == {'bat', 'lat', 'lon', 'provider'}

        decrypted_location = LocationData.decrypt(encrypted_location, client_device_data)
        assert decrypted_location == plain_location
