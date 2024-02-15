from Crypto.Random import get_random_bytes
from Crypto.Hash import SHA512
from Crypto.Protocol.KDF import PBKDF2
from Crypto.Cipher import AES

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization

from config import SALT_2


def generate_key_pair():
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
        backend=default_backend()
    )

    public_key = private_key.public_key()

    pem_private_key = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    )

    pem_public_key = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )

    return pem_public_key.decode('utf-8'), pem_private_key.decode('utf-8')


def generate_master_key(password: str):
    salt = SALT_2
    key = PBKDF2(password, salt, 16, hmac_hash_module=SHA512)
    return key


def encrypt(key: bytes, message: str):
    message = message.encode()
    nonce = get_random_bytes(12)
    cipher = AES.new(key, AES.MODE_GCM, nonce)
    ciphertext, tag = cipher.encrypt_and_digest(message)
    encrypted_data = ciphertext + nonce + tag
    return encrypted_data


def decrypt(key: bytes, data: str):
    data = bytes.fromhex(data)
    tag = data[-16:]
    nonce = data[-28:-16]
    encrypted_data = data[:-28]
    cipher = AES.new(key, AES.MODE_GCM, nonce=nonce)
    decrypted_data = cipher.decrypt_and_verify(encrypted_data, tag)
    return decrypted_data.decode()