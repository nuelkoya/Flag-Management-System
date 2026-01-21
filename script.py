import requests
from config import get_settings

settings = get_settings()
BASE_URL = 'http://127.0.0.1:8000'
USER_CREDENTIALS = {
    "username": "test1@gmail.com",
    "password": settings.user_password
}



def get_authorized_session():
    session = requests.Session()

    response = session.post(f"{BASE_URL}/login", data=USER_CREDENTIALS)

    if response.status_code != 200:
        print(f"Login failed: {response.text}")
        return None

    token = response.json().get('access_token')

    session.headers.update({
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    })

    return session



def rate_test():
    client = get_authorized_session()

    if not client:
        return 
    
    for i in range(10):
        response = client.get(f'{BASE_URL}/flags')
        print(response.status_code)
        print(response.json())

if __name__ == "__main__":
    rate_test()

