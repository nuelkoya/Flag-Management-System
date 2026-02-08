import pytest
from dependencies import verify_admin_token
from fastapi import FastAPI, Depends
from fastapi.testclient import TestClient
from fastapi.exceptions import HTTPException




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

    

