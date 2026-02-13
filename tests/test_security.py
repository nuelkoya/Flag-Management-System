import pytest
from pwdlib import PasswordHash
from security import verify_password
hasher = PasswordHash.recommended()
FAKE_PWD = "Test1P@ss"
FAKE_HASH = hasher.hash(FAKE_PWD)
DUMMY_HASH = hasher.hash("Dummy12@")

def test_verify_password():
    result = verify_password(
        plain_password = FAKE_PWD,
        hashed_password = FAKE_HASH
    )
    assert result is True

@pytest.mark.parametrize("password,hashed_password", [
    (FAKE_PWD, DUMMY_HASH), ("FakePass!1", FAKE_HASH)
])
def test_verify_password_invalid(password, hashed_password):
    result = verify_password(
        plain_password = password,
        hashed_password = hashed_password
    )
    assert result is False

