import pytest
from restllm.models.authentication import ChangePassword


def test_passwords_match():
    data = {
        "old_password": "oldpassword123",
        "new_password": "newpassword123",
        "confirm_new_password": "newpassword123",
    }
    model = ChangePassword(**data)
    assert model.new_password.get_secret_value() == data["new_password"]
    assert model.confirm_new_password.get_secret_value() == data["confirm_new_password"]


def test_passwords_do_not_match():
    data = {
        "old_password": "oldpassword123",
        "new_password": "newpassword123",
        "confirm_new_password": "differentpassword123",
    }
    with pytest.raises(ValueError):
        ChangePassword(**data)


def test_new_passwords_are_empty():
    data = {
        "old_password": "oldpassword123",
        "new_password": None,
        "confirm_new_password": None,
    }
    with pytest.raises(ValueError):
        ChangePassword(**data)
