import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock
from main import app
from security import get_current_user
from dependencies import verify_admin_token, get_flags, toggle_flag
from database import get_session
from config import get_settings

mock_flag_data = [
    {
        "name": "Testadmin",
        "is_enabled": False,
        "description": "Testadmin created a flag!!",
        "environment": "prod",
    }
]



@pytest.fixture()
def client():
    return TestClient(app)


@pytest.fixture()
def settings():
    return get_settings()


class MockUser:
    def __init__(self, id, username):
        self.id = id
        self.username = username



@pytest.fixture
def mock_admin():
    user = MockUser(id=1, username="testadmin")

    app.dependency_overrides[get_current_user] = lambda: user
    app.dependency_overrides[get_session] = lambda: MagicMock()
    app.dependency_overrides[get_flags] = lambda : mock_flag_data
    app.dependency_overrides[toggle_flag] = lambda : mock_flag_data[0]
    
    yield user 
    
    app.dependency_overrides = {}


@pytest.fixture
def mock_flag_data_list():
    return mock_flag_data

@pytest.fixture
def mock_flag_data_dict():
    return mock_flag_data[0]