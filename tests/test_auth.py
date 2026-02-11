import pytest
from unittest.mock import MagicMock
from pwdlib import PasswordHash
from routers.auth import authenticate_user

hasher = PasswordHash.recommended()
FAKE_PASSWORD = "fake1password"
HASHED_PASSWORD = hasher.hash(FAKE_PASSWORD)

class User:
    def __init__(self, username, HASHED_PASSWORD):
        self.username = username
        self.hashed_password = HASHED_PASSWORD

testUser = User("testadmin@example.com", HASHED_PASSWORD)  

def test_authenticate_user_success():
    mock_session = MagicMock()
    mock_session.exec.return_value.scalar.return_value = testUser

    result = authenticate_user(
        session = mock_session,
        username = testUser.username,
        password = FAKE_PASSWORD
    )
    assert result.username == "testadmin@example.com"


@pytest.mark.parametrize("password,user, label", [
    ("some1pass", testUser, "Incorrect password"), (FAKE_PASSWORD, None, "User not found")
])
def test_authenticate_user_failure(password, user, label):
    mock_session = MagicMock()
    mock_session.exec.return_value.scalar.return_value = user
  
    result = authenticate_user(
        session = mock_session,
        username = "test-user",
        password = password
    )

    assert result is False, f"Failed on case:{label}"
