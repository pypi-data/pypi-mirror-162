import base64
import logging
import secrets
from hashlib import pbkdf2_hmac
from typing import Union

from Cryptodome.Cipher import AES, PKCS1_v1_5
from Cryptodome.PublicKey import RSA
from Cryptodome.Util.Padding import pad, unpad

from fmd_client.constants import FMD_BLOCK_SIZE, FMD_ITERATIONS, FMD_PASSWORD_SALT


logger = logging.getLogger(__name__)


def base64_encode(data: Union[bytes, str]) -> str:
    """
    >>> base64_encode(b'foo')
    'Zm9v'
    """
    base64_bytes = base64.b64encode(data)
    return base64_bytes.decode(encoding='utf-8')


def fmd_pbkdf2_hmac(raw_password: str, salt: bytes, iterations: int) -> bytes:
    key: bytes = pbkdf2_hmac(
        hash_name='sha1',
        password=bytes(raw_password, encoding='utf-8'),
        salt=salt,
        iterations=iterations,
        dklen=32,
    )
    return key


def generate_hashed_password(raw_password: str):
    """
    Generate a hashed password in the same way as the FMD web page and app.

    >>> generate_hashed_password(raw_password='foo')
    '06760f52af81bfe8f9406a65fda7f7b16484e91c55beaa36e5a1209985ffb0ee'

    https://gitlab.com/Nulide/findmydeviceserver/-/blob/master/web/logic.js
    """
    hashed_password_bytes = fmd_pbkdf2_hmac(
        raw_password,
        salt=FMD_PASSWORD_SALT,
        iterations=FMD_ITERATIONS * 2,  # == 3734
    )
    hashed_password_hex = hashed_password_bytes.hex()
    return hashed_password_hex


def decrypt_aes(*, cipher_text: str, raw_password: str) -> bytes:
    key_size = 256
    iv_size = 128

    iv_length = iv_size // 4  # == 32
    salt_length = key_size // 4  # == 64

    salt_hex = cipher_text[:salt_length]
    salt_bytes = bytes.fromhex(salt_hex)
    assert len(salt_bytes) == 32

    iv_hex = cipher_text[salt_length : (salt_length + iv_length)]
    iv_bytes = bytes.fromhex(iv_hex)
    assert len(iv_bytes) == 16

    encrypted_base64 = cipher_text[(salt_length + iv_length) :]
    ciphertext = base64.b64decode(encrypted_base64)

    hashed_password_bytes = fmd_pbkdf2_hmac(
        raw_password, salt=salt_bytes, iterations=FMD_ITERATIONS
    )

    aes_cipher = AES.new(key=hashed_password_bytes, mode=AES.MODE_CBC, iv=iv_bytes)
    plaintext_bytes = aes_cipher.decrypt(ciphertext)
    plaintext_bytes = unpad(plaintext_bytes, block_size=16)
    return plaintext_bytes


def encrypt_aes(*, plaintext_bytes: bytes, raw_password: str) -> str:
    key_size = 256
    iv_size = 128

    iv_nbytes = iv_size // 8  # == 16
    salt_nbytes = key_size // 8  # == 32

    salt_bytes = secrets.token_bytes(nbytes=salt_nbytes)
    assert len(salt_bytes) == 32

    iv_bytes = secrets.token_bytes(nbytes=iv_nbytes)
    assert len(iv_bytes) == 16

    hashed_password_bytes = fmd_pbkdf2_hmac(
        raw_password, salt=salt_bytes, iterations=FMD_ITERATIONS
    )

    aes_cipher = AES.new(key=hashed_password_bytes, mode=AES.MODE_CBC, iv=iv_bytes)

    plaintext_bytes_padded = pad(plaintext_bytes, block_size=FMD_BLOCK_SIZE, style='pkcs7')

    ciphertext = aes_cipher.encrypt(plaintext_bytes_padded)
    encrypted_base64 = base64_encode(ciphertext)
    cipher_text = salt_bytes.hex() + iv_bytes.hex() + encrypted_base64
    return cipher_text


def decrypt(*, data_base64: str, raw_private_key: str, raw_password: str) -> str:
    private_key = decrypt_aes(raw_password=raw_password, cipher_text=raw_private_key)

    rsa_key = RSA.import_key(private_key)
    rsa_cipher = PKCS1_v1_5.new(rsa_key)

    ciphertext = base64.b64decode(data_base64)

    decrypted_data_bytes = rsa_cipher.decrypt(ciphertext, sentinel='Decrypt Error')
    plaintext = decrypted_data_bytes.decode(encoding='utf-8')
    return plaintext


def encrypt(*, plaintext: str, raw_private_key: str, raw_password: str) -> str:
    private_key = decrypt_aes(raw_password=raw_password, cipher_text=raw_private_key)

    rsa_key = RSA.import_key(private_key)
    rsa_cipher = PKCS1_v1_5.new(rsa_key)

    data_bytes = bytes(plaintext, encoding='utf-8')
    decrypted_data_bytes = rsa_cipher.encrypt(data_bytes)
    decrypted_data_base64 = base64_encode(decrypted_data_bytes)
    return decrypted_data_base64


def generate_keys(raw_password: str) -> (str, str):
    logger.info('Generate new RSA keys')

    key = RSA.generate(2048)
    private_key = key.export_key()

    encrypted_private_key = encrypt_aes(
        plaintext_bytes=private_key + b'\n',
        raw_password=raw_password,
    )

    raw_public_key = key.publickey().export_key()
    public_key_base64_bytes = base64.b64encode(raw_public_key)
    public_key_base64_str = public_key_base64_bytes.decode(encoding='utf-8')

    return encrypted_private_key, public_key_base64_str
