from Crypto.Random import get_random_bytes
from Crypto.Hash import SHA512
from Crypto.Protocol.KDF import PBKDF2
from Crypto.Cipher import AES

from config import SALT_2


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