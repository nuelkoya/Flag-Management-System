import pytest
from unittest.mock import MagicMock
from starlette.requests import Request
from pwdlib import PasswordHash
from fastapi.exceptions import HTTPException
from pydantic import BaseModel, EmailStr
from routers.auth import authenticate_user, sign_up
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

mock_user_create_data ={

}

class TestUserCreateModel(BaseModel):
    email: EmailStr
    password: str

@pytest.fixture
def create_test_user():
    return TestUserCreateModel(
        email="test@gmail.com",
        password="ValidPassword123!"
    )


@pytest.fixture
def create_test_user_invalid():
    return TestUserCreateModel(
        email="test@gmail.com",
        password="ValidPassword123"
    )

def test_sign_up(create_test_user):
    mock_session = MagicMock()
    mock_session.exec.return_value.first.return_value = None
    mock_request = MagicMock(spec=Request)
    
    result = sign_up (
        request=mock_request,
        user = create_test_user,
        session= mock_session
    )

    assert result["user"] == create_test_user.email
    assert result["message"] == "User created!"
    assert mock_session.add.called is True
    assert mock_session.commit.called is True
    assert mock_session.refresh.called is True
    added_user = mock_session.add.call_args[0][0]
    assert added_user.email == create_test_user.email



def test_sign_up_invalid_password(create_test_user_invalid):
    mock_session = MagicMock()
    mock_session.exec.return_value.first.return_value = None
    mock_request = MagicMock(spec=Request)
    
    with pytest.raises(HTTPException) as exc:
        sign_up (
            request=mock_request,
            user = create_test_user_invalid,
            session= mock_session
        )
    
    assert exc.value.status_code == 409
    assert  "at least 8 characters long" in exc.value.detail

