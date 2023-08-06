import dataclasses

from fmd_client.crypto import decrypt, encrypt


@dataclasses.dataclass
class ClientDeviceData:
    plaintext_password: str = None
    hashed_password: str = None
    device_id: str = None
    short_id: str = None
    encrypted_private_key: str = None
    public_key_base64_str: str = None


@dataclasses.dataclass
class LocationDataSize:
    length: int = None
    beginning: int = None


@dataclasses.dataclass
class LocationData:
    bat: str = None
    lat: str = None
    lon: str = None
    provider: str = None
    date: int = None
    encrypted: bool = None

    @classmethod
    def decrypt(cls, location, client_device_data: ClientDeviceData):
        assert isinstance(location, cls)
        assert location.encrypted is True
        assert client_device_data.encrypted_private_key
        assert client_device_data.plaintext_password

        def _decrypt(data_base64):
            return decrypt(
                data_base64=data_base64,
                raw_private_key=client_device_data.encrypted_private_key,
                raw_password=client_device_data.plaintext_password,
            )

        return cls(
            bat=_decrypt(location.bat),
            lat=_decrypt(location.lat),
            lon=_decrypt(location.lon),
            provider=_decrypt(location.provider),
            date=location.date,
            encrypted=False,
        )

    @classmethod
    def encrypt(cls, location, client_device_data: ClientDeviceData):
        assert isinstance(location, cls)
        assert location.encrypted is False
        assert client_device_data.encrypted_private_key
        assert client_device_data.plaintext_password

        def _encrypt(plaintext):
            return encrypt(
                plaintext=plaintext,
                raw_private_key=client_device_data.encrypted_private_key,
                raw_password=client_device_data.plaintext_password,
            )

        return cls(
            bat=_encrypt(location.bat),
            lat=_encrypt(location.lat),
            lon=_encrypt(location.lon),
            provider=_encrypt(location.provider),
            date=location.date,
            encrypted=True,
        )
