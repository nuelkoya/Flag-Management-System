import requests

jwt_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ0ZXN0MkBnbWFpbC5jb20iLCJleHAiOjE3Njc3NTYzMzh9.q7dtIb7q19YI3K1wtkvNTj0r2CX1zePTZ3qAn_fOK-A"
headers = {
    "Authorization": f"Bearer {jwt_token}",
    "Content-Type": "application/json"
}

def rate_test():
    for i in range(10):
        response = requests.get('http://127.0.0.1:8000/flags', headers=headers)
        print(response.status_code)
        print(response.json())
rate_test()