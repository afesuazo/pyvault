from Crypto.Hash import SHA512
from Crypto.Protocol.KDF import PBKDF2

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes

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


def encrypt_with_key(public_key: str, data: str) -> bytes:
    public_key = serialization.load_pem_public_key(public_key.encode(), backend=default_backend())
    encrypted_data = public_key.encrypt(
        data.encode(),
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    return encrypted_data
