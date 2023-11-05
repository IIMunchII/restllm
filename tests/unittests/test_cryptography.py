import pytest
from cryptography.fernet import Fernet

from restllm.cryptography.secure_url import (
    decrypt_payload,
    encrypt_payload,
    generate_secure_url,
    payload_is_valid,
)


@pytest.fixture
def test_fernet_instance() -> Fernet:
    return Fernet(Fernet.generate_key())


@pytest.fixture
def test_payload() -> dict:
    return {
        "user_id": "user_123",
        "resource_id": "resource_456",
    }


def test_generate_secure_url(test_fernet_instance, test_payload):
    parsed_url_data = generate_secure_url(test_fernet_instance, test_payload)

    is_valid = payload_is_valid(
        parsed_url_data["payload"],
        parsed_url_data["signature"],
    )
    assert is_valid, "Failed to verify encrypted payload against signature"


def test_decrypt_payload(test_fernet_instance, test_payload):
    encrypted_payload = encrypt_payload(test_fernet_instance, test_payload)
    decrypted_payload = decrypt_payload(test_fernet_instance, encrypted_payload)
    assert (
        test_payload == decrypted_payload
    ), f"{decrypt_payload} failed to decrypt object into expected dictionary: {test_payload}"
