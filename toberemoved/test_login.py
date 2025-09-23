import requests
import json

url = "http://localhost:5000/api/auth/login"
headers = {'Content-Type': 'application/json'}
data = {
    "username": "admin",
    "password": "admin123"
}

response = requests.post(url, headers=headers, data=json.dumps(data))
print(f"Status Code: {response.status_code}")
print(f"Response: {response.text}")
