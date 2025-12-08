import requests
import pytest
import uuid

BASE_URL = "http://localhost:8000"

def test___get_all_vehicles(headers: dict) -> None:
    response = requests.get(f"{BASE_URL}/vehicles", headers=headers)
    assert response.status_code == 200

def test_add_vehicle(headers: dict) -> None:
    unique_id = str(uuid.uuid4())[:6].upper()
    payload = {
        "license_plate": f"AAC{unique_id}",
        "make": "Toyoata",
        "model": "Codrolla",
        "color": "Red",
        "year": 2020
    }
    response = requests.post(f"{BASE_URL}/vehicles", headers=headers, json=payload)
    assert response.status_code in [200, 201], f"Unexpected response: {response.status_code}, {response.text}"

def test_get_vehicle(headers : dict) -> None:
    unique_id = str(uuid.uuid4())[:6].upper()
    payload = {
        "license_plate": f"BCC{unique_id}",
        "make": "Honda",
        "model": "Civic",
        "color": "Blue",
        "year": 2021
    }

    response = requests.post(f"{BASE_URL}/vehicles", headers=headers, json=payload)
    response_json = response.json()
    vehicle_id = response_json["id"]

    response = requests.get(f"{BASE_URL}/vehicles/{vehicle_id}", headers=headers)
    assert response.status_code == 200

def test_update_vehicle(headers: dict) -> None:
    unique_id = str(uuid.uuid4())[:6].upper()
    payload = {
        "license_plate": f"ASA{unique_id}",
        "make": "Ford",
        "model": "Focus",
        "color": "Black",
        "year": 2019
    }
    response = requests.post(f"{BASE_URL}/vehicles", headers=headers, json=payload)
    json_response = response.json()
    vehicle_id = json_response["id"]

    unique_id2 = str(uuid.uuid4())[:6].upper()
    payload = {
        "license_plate": f"ASA{unique_id2}",
        "make": "Ford",
        "model": "Fiesta",
        "color": "Green",
        "year": 2020
    }
    response = requests.put(f"{BASE_URL}/vehicles/{vehicle_id}", headers=headers, json=payload)
    assert response.status_code == 200

def test_deleting_vehicle(headers: dict) -> None:
    unique_id = str(uuid.uuid4())[:6].upper()
    payload = {
        "license_plate": f"SSA{unique_id}",
        "make": "Nissan",
        "model": "Altima",
        "color": "White",
        "year": 2021
    }
    response = requests.post(f"{BASE_URL}/vehicles", headers=headers, json=payload)
    vehicle_id = response.json()["id"]

    response = requests.delete(f"{BASE_URL}/vehicles/{vehicle_id}", headers=headers)
    assert response.status_code == 200

def test_get_vehicles_no_auth():
    payload = {"username": "", "password": ""}
    response = requests.post(f"{BASE_URL}/login", json=payload)
    json_response = response.json()
    access_token = json_response.get("access_token", "")
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get(f"{BASE_URL}/vehicles", headers=headers)
    assert response.status_code != 200

def delete_non_existing_vehicle(headers: dict) -> None:
    response = requests.delete(f"{BASE_URL}/vehicles/1000", headers=headers)
    assert response.status_code == 404

def test__get_non_existing_vehicle(headers: dict) -> None:
    response = requests.get(f"{BASE_URL}/vehicles/1111", headers=headers)
    assert response.status_code == 200

def test_update_non_existing_vehicle(headers: dict) -> None:
    payload = {
        "license_plate": "NON123",
        "make": "Honda",
        "model": "Civic",
        "color": "Yellow",
        "year": 2021
    }
    response = requests.put(f"{BASE_URL}/vehicles/111", headers=headers, json=payload)
    assert response.status_code == 404

def test_update_empty_string(headers: dict) -> None:
    payload = {
        "license_plate": "",
        "make": "",
        "model": "",
        "color": "",
        "year": 0
    }
    response = requests.put(f"{BASE_URL}/vehicles/111", headers=headers, json=payload)
    assert response.status_code >= 400
