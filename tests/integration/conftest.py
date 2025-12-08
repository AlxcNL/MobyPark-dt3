import pytest
import requests
import uuid

BASE_URL = "http://localhost:8000"

@pytest.fixture(scope="session")
def headers() -> dict:
    # Try to create an admin user with a unique name to avoid conflicts
    unique_id = str(uuid.uuid4())[:8]
    username = f"admin_{unique_id}"

    register_payload = {
        "username": username,
        "email": f"{username}@example.com",
        "password": "strongpassword123",
        "name": "Admin User",
        "phone": "+1234567890",
        "birth_year": 1990,
        "role": "admin"
    }
    try:
        response = requests.post(f"{BASE_URL}/register", json=register_payload)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        # If registration fails, try with the existing johndoe account
        username = "johndoe"

    login_payload = {
        "username": username,
        "password": "strongpassword123"
    }
    response = requests.post(f"{BASE_URL}/login", json=login_payload)
    response.raise_for_status()
    token = response.json().get("access_token")

    return {"Authorization": f"Bearer {token}"}
