import requests
import uuid

BASE_URL = "http://localhost:8000/v2"


# happy flow
def test_create_user():
    unique_id = str(uuid.uuid4())[:8]
    payload = {
        "username": f"testuser_{unique_id}",
        "email": f"testuser_{unique_id}@example.com",
        "password": "strongpassword123",
        "name": "Test User",
        "phone": "+1234567891",
        "birth_year": 1990,
    }
    response = requests.post(f"{BASE_URL}/register", json=payload)

    assert response.status_code == 200


def test_login():
    unique_id = str(uuid.uuid4())[:8]
    user_payload = {
        "username": f"testuser_{unique_id}",
        "email": f"testuser_{unique_id}@example.com",
        "password": "strongpassword123",
        "name": "Test User",
        "phone": "+1234567891",
        "birth_year": 1990,
    }
    requests.post(f"{BASE_URL}/register", json=user_payload)

    login_payload = {"username": user_payload["username"], "password": "strongpassword123"}
    response = requests.post(f"{BASE_URL}/login", json=login_payload)

    assert response.status_code == 200

def test_logout() -> None:
    unique_id = str(uuid.uuid4())[:8]
    user_payload = {
        "username": f"testuser_{unique_id}",
        "email": f"testuser_{unique_id}@example.com",
        "password": "strongpassword123",
        "name": "Test User",
        "phone": "+1234567891",
        "birth_year": 1990,
    }
    requests.post(f"{BASE_URL}/register", json=user_payload)

    login_payload = {"username": user_payload["username"], "password": "strongpassword123"}
    login_response = requests.post(f"{BASE_URL}/login", json=login_payload)
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    response = requests.post(f"{BASE_URL}/logout", headers=headers)
    assert response.status_code == 200

# sad flow
def test_create_user_null_name():
    payload = {"username": "", "password": "secret"}
    response = requests.post(f"{BASE_URL}/register", json=payload)

    assert response.status_code != 200


def test_create_user_null_password():
    payload = {"username": "", "password": ""}
    response = requests.post(f"{BASE_URL}/register", json=payload)

    assert response.status_code != 200


def test_wrong_token():
    response = requests.get(f"{BASE_URL}/vehicles", headers={"Authorization": "Bearer dujshdsj"})

    assert response.status_code == 401


def test_duplicate_create_user():
    unique_id = str(uuid.uuid4())[:8]
    payload = {
        "username": f"testuser_{unique_id}",
        "email": f"testuser_{unique_id}@example.com",
        "password": "strongpassword123",
        "name": "Test User",
        "phone": "+1234567891",
        "birth_year": 1990,
    }
    requests.post(f"{BASE_URL}/register", json=payload)
    response = requests.post(f"{BASE_URL}/register", json=payload)

    assert response.status_code == 400
