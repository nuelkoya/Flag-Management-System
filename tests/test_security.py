from unittest.mock import MagicMock, patch
import pytest
import jwt
from jwt import PyJWTError
from datetime import timedelta
from pwdlib import PasswordHash
from fastapi.exceptions import HTTPException
from security import verify_password, get_password_hash, create_access_token, get_current_user


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


def test_get_password_hash():
    result = get_password_hash(
        password=FAKE_PWD
    )
    assert "$argon" in result


def test_get_password_hash_empty():
    result = get_password_hash(
        password=""
    )
    assert "$argon" in result


def test_create_access_token_custom():
    fake_data = {
        "sub": "test1@example.com"
    }

    result = create_access_token(
        data = fake_data,
        expires_delta = timedelta(minutes=5)
    )
    assert len(result) > 20



def test_create_access_token_default():
    fake_data = {
        "email": "test1@example.com"
    }
    
    result = create_access_token(
        data = fake_data,
        expires_delta = None
    )
    assert len(result) > 20



def test_create_access_token_missing_data():
    with pytest.raises(AttributeError) as exc:
        create_access_token(
            data = None,
            expires_delta = None
        )
    
    assert "NoneType" in str(exc.value) 


def test_get_current_user():
    mock_session = MagicMock()
    fake_user = MagicMock()
    fake_user.email = "test1@example.com"

    mock_session.exec.return_value.scalar.return_value = fake_user

    fake_payload={"sub": "test1@example.com"}
    with patch("jwt.decode", return_value=fake_payload):
        result = get_current_user(
            session=mock_session,
            token="fake-token-string" 
        )
   
    assert result.email == "test1@example.com"
    mock_session.exec.assert_called_once()


def test_get_current_user_invalid_token():
    mock_session = MagicMock()

    with patch("jwt.decode", side_effect=PyJWTError):
        with pytest.raises(HTTPException) as exc:
            get_current_user(session=mock_session, token="bad-token")
    
    assert exc.value.status_code == 401
    assert exc.value.detail == "Could not validate credentials"
    


