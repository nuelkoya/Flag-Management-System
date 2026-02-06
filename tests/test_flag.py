import pytest
from unittest.mock import MagicMock
from main import app
from database import get_session


def test_get_flags(client, mock_admin):
    response = client.get("/flags/")
    assert response.status_code == 200
    assert response.json()["message"] == "Flags"


def test_get_flags_unauthenticated(client):
    response = client.get("/flags/")
    assert response.status_code == 401
    assert response.json() == {"detail": "Not authenticated"}
    

def test_create_flag(settings, client, mock_admin, mock_flag_data_dict):
    header = {"x-admin-token" : settings.x_admin_token}
    payload = mock_flag_data_dict
    response = client.post("/flags/", headers=header, json=payload)
    assert response.status_code == 200
    assert response.json()["name"] == payload["name"]
    assert response.json()["is_enabled"] == payload["is_enabled"]
    assert response.json()["environment"] == payload["environment"]
    assert response.json()["description"] == payload["description"]


def test_create_flag_unauthenticated(client,  mock_flag_data_dict):
    payload = mock_flag_data_dict
    response = client.post("/flags/", json=payload)
    assert response.status_code == 401
    assert response.json() == {"detail": "Not authenticated"}


def test_create_flag_unauthorized(client, mock_admin,  mock_flag_data_dict):
    header = { "x-admin-token" : "rubbishtoken"}
    payload = mock_flag_data_dict
    response = client.post("/flags/", headers=header, json=payload)
    assert response.status_code == 403
    assert response.json() == {"detail": "Invalid Secret Header"}


def test_create_flag_invalid_data(client,  mock_admin,):
    invalid_payload = {
        "name": "Testadmin",
        "description": "Testadmin created a flag!!",
        "is_enabled" : True
    }

    response = client.post("/flags/", json=invalid_payload)
    assert response.status_code == 400


@pytest.mark.parametrize("environment", [('prod'), ('stage')])
def test_update_flag(client, mock_admin, environment):
    flag_name = "Testadmin"
    response = client.patch(f"/flags/{environment}/{flag_name}")
    assert response.status_code == 200
    

@pytest.mark.parametrize("environment", [('prod'), ('stage')])
def test_update_flag_invalid_flag_name(client, mock_admin, environment):
    flag_name = ""
    response = client.patch(f"/flags/{environment}/{flag_name}")
    print(environment)
    assert response.status_code == 404
    assert response.json() == {"detail":"Not Found"}

@pytest.mark.parametrize("environment", [('prod'), ('stage')])
def test_update_flag_unauthenticated(client, environment):
    flag_name = "Testadmin"
    response = client.patch(f"/flags/{environment}/{flag_name}")
    assert response.status_code == 401
    assert response.json() == {"detail": "Not authenticated"}


@pytest.fixture
def mock_session_scaler():
    mock_session =  MagicMock()
    mock_session.exec.return_value.scalar.return_value = MagicMock() 
    app.dependency_overrides[get_session] = lambda: mock_session


@pytest.mark.parametrize("environment", [('prod'), ('stage')])
def test_delete_flag(client, mock_admin, mock_session_scaler, settings, environment, mock_flag_data_dict):
    flag_name = mock_flag_data_dict['name']
    headers = {"x-admin-token": settings.x_admin_token}
    response = client.delete(f"/flags/{environment}/{flag_name}", headers=headers)
    assert response.status_code == 200
    assert response.json() == {"ok": True}


@pytest.mark.parametrize("environment", [('prod'), ('stage')])
def test_delete_flag_unauthorized(client, mock_admin, mock_session_scaler, environment, mock_flag_data_dict):
    flag_name = mock_flag_data_dict['name']
    response = client.delete(f"/flags/{environment}/{flag_name}")
    assert response.status_code == 400
    assert response.json()["error"][0]["msg"] == "Field required"

@pytest.mark.parametrize("environment", [('prod'), ('stage')])
def test_delete_flag_unauthenticated(client,  mock_session_scaler, environment, mock_flag_data_dict):
    flag_name = mock_flag_data_dict['name']
    response = client.delete(f"/flags/{environment}/{flag_name}")
    assert response.status_code == 401
    assert response.json() == { "detail": "Not authenticated" }
    
    




    
    