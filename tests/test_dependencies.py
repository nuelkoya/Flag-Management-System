from unittest.mock import MagicMock
import pytest
from fastapi import FastAPI, Depends
from fastapi.testclient import TestClient
from fastapi.exceptions import HTTPException
from sqlalchemy.exc import SQLAlchemyError
from dependencies import verify_admin_token, get_flags_dep, toggle_flag, delete_flag_dep


def test_verify_admin_token_unit_valid(settings):
    result = verify_admin_token(settings.x_admin_token, settings)
    assert result is True

def test_verify_admin_token_unit_invalid(settings):
    with pytest.raises(HTTPException) as exc:
        verify_admin_token("wrong-secret", settings)

    assert exc.value.status_code == 403
    assert exc.value.detail == "Invalid Secret Header"

    

def test_verify_admin_token(settings):
    tmp_app = FastAPI()
    
    @tmp_app.get("/check")
    def check_route(authorized: bool = Depends(verify_admin_token)):
        return {"ok": True}
    
    client = TestClient(tmp_app)

    response = client.get("/check", headers={"x-admin-token": settings.x_admin_token})
    assert response.status_code == 200
    assert response.json() == {"ok": True}


    response = client.get("/check", headers={"x-admin-token": "wrong-secret-key"})
    assert response.status_code == 403
    assert response.json()["detail"] == "Invalid Secret Header"

    
    response = client.get("/check")
    assert response.status_code == 422

    

def test_get_flags_dep(mock_flag_data_list):
    mock_session = MagicMock()
    mock_session.exec.return_value.scalars.return_value.all.return_value  = mock_flag_data_list
    
    result = get_flags_dep (
        session = mock_session,
        environment = mock_flag_data_list[0]["environment"],
        enabled = mock_flag_data_list[0]["is_enabled"],
        offset = 0,
        limit = 10
    )

    assert len(result) == 1
    assert mock_session.exec.called
    assert result == mock_flag_data_list


@pytest.mark.parametrize("offset, limit", [(0, "100"), ("2", 5), ("3", "10")])
def test_get_flags_dep_invalid(mock_flag_data_list, offset, limit):
    mock_session = MagicMock()
    mock_session.exec.return_value.scalars.return_value.all.return_value = mock_flag_data_list
    

    with pytest.raises(TypeError) as exc:
        get_flags_dep (
            session = mock_session,
            environment = mock_flag_data_list[0]["environment"],
            enabled = mock_flag_data_list[0]["is_enabled"],
            offset = offset,
            limit = limit
        )
    assert str(exc.value) == "Offset and Limit must be integers"


def test_get_flags_dep_db_failure(mock_flag_data_list):
    mock_session = MagicMock()
    mock_session.exec.return_value.scalars.return_value.all.side_effect = SQLAlchemyError("Database connection lost") 
    
    with pytest.raises(SQLAlchemyError) as exc:
        get_flags_dep (
            session = mock_session,
            environment = "prod",
            enabled = False,
            offset = 0,
            limit = 10
        )
    assert str(exc.value) == "Database connection lost"
    assert mock_session.exec.called


def test_toggle_flag(user):
    mock_session = MagicMock()
    fake_flag = MagicMock(is_enabled = False)
    mock_session.exec.return_value.scalar.return_value = fake_flag
    result = toggle_flag(
        session=mock_session,
        flag_name="test-flag",
        environment="prod",
        current_user=user,
    )
    assert fake_flag.is_enabled == True
    assert mock_session.add.called
    assert mock_session.commit.called


def test_toggle_flag_db_failure(user):
    mock_session = MagicMock()
    mock_session.exec.return_value.scalar.side_effect = SQLAlchemyError("Database connection lost")
    with pytest.raises(SQLAlchemyError, match = "Database connection lost") as exc:
        toggle_flag(
            session=mock_session,
            flag_name="test-flag",
            environment="prod",
            current_user=user,
            _=True
        )
    assert mock_session.commit.called is False


def test_delete_flag_dep(user):
    mock_session = MagicMock()
    fake_flag = MagicMock()
    mock_session.exec.return_value.scalar.return_value = fake_flag

    result = delete_flag_dep (
        session = mock_session,
        flag_name= "test-flag",
        environment = "prod",
        current_user = user,
        _ = True
    )

    mock_session.delete.assert_called_once_with(fake_flag)
   
    assert result == {"ok": True}
    assert mock_session.delete.called
    assert mock_session.commit.called

    
def test_delete_flag_dep_not_found(user):
    mock_session = MagicMock()
    fake_flag = MagicMock()
    mock_session.exec.return_value.scalar.return_value = None

    with pytest.raises(HTTPException) as exc:
        delete_flag_dep (
            session = mock_session,
            flag_name= "test-flag",
            environment = "stage",
            current_user = user,
            _ = True
        )


    assert str(exc.value) != {"ok": True}
    assert exc.value.status_code == 404
    assert exc.value.detail == "Flag not found or unauthorized"
    assert not mock_session.delete.called
    assert not mock_session.commit.called

    
    
   