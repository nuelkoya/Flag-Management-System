from datetime import timedelta
import pytest
from unittest.mock import MagicMock, patch
from starlette.requests import Request
from pwdlib import PasswordHash
from fastapi.exceptions import HTTPException
from pydantic import BaseModel, EmailStr
from routers.auth import authenticate_user, sign_up, login
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

class UserCreateTestModel(BaseModel):
    email: EmailStr
    password: str


class LoginTestModel(BaseModel):
    username: str
    password: str

@pytest.fixture
def create_test_user():
    return UserCreateTestModel(
        email="test@gmail.com",
        password="ValidPassword123!"
    )


@pytest.fixture
def create_test_user_invalid():
    return UserCreateTestModel(
        email="test@gmail.com",
        password="ValidPassword123"
    )

@pytest.fixture
def login_test_user():
    return LoginTestModel(
        username="test@gmail.com",
        password="ValidPassword123!"
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


def test_login(login_test_user):
    mock_session = MagicMock()
    mock_db_user = MagicMock()
    mock_db_user.email = "test@gmail.com"
    mock_db_user.hashed_password = "fake_hash_string"
    mock_session.exec.return_value.first.return_value = mock_db_user

    with patch("routers.auth.authenticate_user", return_value = mock_db_user):
        result = login(
            form_data = login_test_user,
            session = mock_session
        )

    assert result["token_type"] == "bearer"
    assert "access_token" in result
 

def test_login_failure(login_test_user):
    mock_session = MagicMock()
   
    with patch("routers.auth.authenticate_user", return_value = None):
        with pytest.raises(HTTPException) as exc:
            login(
                form_data = login_test_user,
                session = mock_session
            )
    
    assert exc.value.status_code == 401
    assert exc.value.detail == "Incorrect username or password"
    assert exc.value.headers["WWW-Authenticate"] == "Bearer"

def test_login_token_expiration(login_test_user):
    mock_session = MagicMock()
    mock_db_user = MagicMock()
    mock_db_user.email = "test@gmail.com"
   
    with patch("routers.auth.authenticate_user", return_value = mock_db_user) as mock_auth:
        with patch("routers.auth.create_access_token", return_value = "fake_jwt_token") as mock_create_token:
        
            result = login(
                form_data = login_test_user,
                session = mock_session
            )

            mock_auth.assert_called_once_with(
                mock_session,
                login_test_user.username,
                login_test_user.password
            )
            _, kwargs = mock_create_token.call_args
            
            
            expected_delta = timedelta(minutes=5) # Match your ACCESS_TOKEN_EXPIRE_MINUTES
        
            assert kwargs["data"]["sub"] == "test@gmail.com"
            assert kwargs["expires_delta"] == expected_delta
            assert result["access_token"] == "fake_jwt_token"
            
