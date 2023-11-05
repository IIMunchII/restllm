import hashlib
import hmac
import json

from cryptography.fernet import Fernet

from ..settings import settings


def encrypt_payload(fernet: Fernet, payload: dict) -> bytes:
    payload_json = json.dumps(payload)
    return fernet.encrypt(payload_json.encode())


def decrypt_payload(fernet: Fernet, encrypted_payload: bytes | str) -> dict:
    decrypted_payload = fernet.decrypt(encrypted_payload)
    return json.loads(decrypted_payload)


def sign_data(data: str) -> str:
    return hmac.new(settings.secret_key.encode(), data, hashlib.sha256).hexdigest()


def signature_is_valid(encrypted_payload: str, received_signature: str) -> bool:
    return (
        hmac.new(
            settings.secret_key.encode(), encrypted_payload, hashlib.sha256
        ).hexdigest()
        == received_signature
    )


def generate_secure_url(fernet: Fernet, payload: dict) -> dict[str, str]:
    encrypted_payload = encrypt_payload(fernet, payload)
    signature = sign_data(encrypted_payload)
    return {"payload": encrypted_payload.decode(), "signature": signature}


def payload_is_valid(encrypted_payload: str, received_signature: str):
    return signature_is_valid(encrypted_payload.encode(), received_signature)
