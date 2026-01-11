import requests

BASE_URL = "http://localhost:8000/v2"

#happy flow
def test_get_profile(headers: dict) -> None:
    response = requests.get(f"{BASE_URL}/profile", headers=headers)
    assert response.status_code == 200

def test_update_profile(headers: dict) -> None:
    payload = {
        "name": "updated",
        "phone": "+31682662864",
        "birth_year": 1999
    }
    response = requests.put(f"{BASE_URL}/profile", headers=headers, json=payload)

    assert response.status_code == 200
#sad slow
def test_updating_profile_validation(headers: dict) -> None:
    payload = {
        "name": 20,
        "phone": "cjenfcfje",
        "birth_year": "1999"
    }
    response = requests.put(f"{BASE_URL}/profile", headers=headers, json=payload)
    assert response.status_code == 422

def test_get_profile_no_auth() -> None:
    response = requests.get(f"{BASE_URL}/profile")
    assert response.status_code == 401  # 401 Unauthorized (no auth token)