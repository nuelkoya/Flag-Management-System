from fastapi.testclient import TestClient
from unittest.mock import MagicMock
from main import app
from security import get_current_user
from dependencies import get_flags, verify_admin_token
from config import get_settings
from database import get_session

client = TestClient(app)
settings = get_settings()

class MockUser:
    def __init__(self, id, username):
        self.id = id
        self.username = username

mock_user = MockUser(id = 1, username = "testadmin")

mock_flag_data = [
    {
        "name": "Testadmin",
        "is_enabled": False,
        "description": "Testadmin created a flag!!",
        "environment": "prod",
    }
]

def test_get_flags():
  
    app.dependency_overrides[get_current_user] = lambda: mock_user
    app.dependency_overrides[get_flags] = lambda: mock_flag_data 
   

    response = client.get("/flags/")
    assert response.status_code == 200
    assert response.json()["message"] == "Flags"

    app.dependency_overrides = {}



def test_create_flag():

    header = {"x-admin-token" : settings.x_admin_token}
    payload = mock_flag_data[0]

    app.dependency_overrides[get_current_user] = lambda: mock_user
    app.dependency_overrides[verify_admin_token] = lambda: settings.x_admin_token 
    app.dependency_overrides[get_session] = lambda: MagicMock() 

    response = client.post("/flags/", headers=header, json=payload)
    assert response.status_code == 200
    assert response.json()["name"] == payload["name"]
    assert response.json()["is_enabled"] == payload["is_enabled"]
    assert response.json()["environment"] == payload["environment"]
    assert response.json()["description"] == payload["description"]
   
    app.dependency_overrides = {}


    
    