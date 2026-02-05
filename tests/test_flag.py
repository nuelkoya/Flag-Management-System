
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





    
    