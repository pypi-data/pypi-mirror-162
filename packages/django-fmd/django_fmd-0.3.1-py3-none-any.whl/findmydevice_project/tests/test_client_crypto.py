from django.test import SimpleTestCase

from findmydevice_project.tests.fixtures import get_fixtures, get_json_fixtures
from fmd_client.crypto import decrypt, decrypt_aes, encrypt, encrypt_aes, generate_keys


class CryptoTestCase(SimpleTestCase):
    def test_decrypt_aes_private_key(self):
        private_key_bytes = decrypt_aes(
            cipher_text=get_fixtures('device1/private_key'),
            raw_password='foo',
        )
        assert private_key_bytes.startswith(b'-----BEGIN RSA PRIVATE KEY-----\n')
        assert private_key_bytes.endswith(b'\n-----END RSA PRIVATE KEY-----\n')

    def test_encrypt_aes(self):
        cipher_text = encrypt_aes(
            plaintext_bytes=b'This is no Secret!',
            raw_password='foo',
        )
        self.assertIsInstance(cipher_text, str)
        private_key_bytes = decrypt_aes(
            cipher_text=cipher_text,
            raw_password='foo',
        )
        self.assertEqual(private_key_bytes, b'This is no Secret!')

    def test_decrypt(self):
        location_data = get_json_fixtures('device1/location1.json')

        def _decrypt(data_base64):
            return decrypt(
                data_base64=data_base64,
                raw_private_key=get_fixtures('device1/private_key'),
                raw_password='foo',
            )

        assert _decrypt(data_base64=location_data['bat']) == '66'
        assert _decrypt(data_base64=location_data['lat']) == '52.516265'
        assert _decrypt(data_base64=location_data['lon']) == '13.37738'
        assert _decrypt(data_base64=location_data['provider']) == 'network'

    def test_encrypt(self):
        plaintext = 'Just a Test äöüß !'
        raw_private_key = get_fixtures('device1/private_key')
        raw_password = 'foo'

        decrypted_data_base64 = encrypt(
            plaintext='Just a Test äöüß !',
            raw_private_key=raw_private_key,
            raw_password=raw_password,
        )
        self.assertIsInstance(decrypted_data_base64, str)
        decrypted_data = decrypt(
            data_base64=decrypted_data_base64,
            raw_private_key=raw_private_key,
            raw_password=raw_password,
        )
        self.assertEqual(decrypted_data, plaintext)

    def test_generate_keys(self):
        raw_private_key, public_key = generate_keys(raw_password='foo')
        private_key_bytes = decrypt_aes(
            cipher_text=raw_private_key,
            raw_password='foo',
        )
        assert private_key_bytes.startswith(b'-----BEGIN RSA PRIVATE KEY-----\n')
        assert private_key_bytes.endswith(b'\n-----END RSA PRIVATE KEY-----\n')

        decrypted_data_base64 = encrypt(
            plaintext='Just a Test äöüß !',
            raw_private_key=raw_private_key,
            raw_password='foo',
        )
        self.assertIsInstance(decrypted_data_base64, str)
        decrypted_data = decrypt(
            data_base64=decrypted_data_base64,
            raw_private_key=raw_private_key,
            raw_password='foo',
        )
        self.assertEqual(decrypted_data, 'Just a Test äöüß !')
