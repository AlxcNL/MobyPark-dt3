import requests
import random
import string

BASE_URL = "http://localhost:8000"

# happy flow
def test_get_all_reservations(headers: dict) -> None:
    response = requests.get(f"{BASE_URL}/reservations", headers=headers)
    assert response.status_code == 200

def test_make_reservation(headers: dict) -> None:
    payload = {
        "license_plate": generate_code(),
        "brand": "Toyota",
        "model": "Corolla",
        "color": "Red"
    }
    vehicle_response = requests.post(f"{BASE_URL}/vehicles", headers=headers, json=payload)
    response_json = vehicle_response.json()

    payload = {
        "vehicles_id": response_json["vehicle_id"],
        "parking_lots_id": 1,
        "start_time": "2020-05-17 00:00:00",
        "end_time": "2020-05-17 12:00:00",
        "status": "confirmed",
        "cost": 10
    }
    response = requests.post(f"{BASE_URL}/reservations", headers=headers, json=payload)
    assert response.status_code == 201, response_json

def test_delete_reservation(headers: dict) -> None:
    vehicle_payload = {
        "license_plate": generate_code(),
        "brand": "Toyota",
        "model": "Corolla",
        "color": "Red"
    }
    vehicle_response = requests.post(f"{BASE_URL}/vehicles", headers=headers, json=vehicle_payload)
    response_json = vehicle_response.json()

    payload = {
        "vehicles_id": response_json["vehicle_id"],
        "parking_lots_id": 1,
        "start_time": "2020-05-17 00:00:00",
        "end_time": "2020-05-17 12:00:00",
        "status": "confirmed",
        "cost": 10
    }
    response = requests.post(f"{BASE_URL}/reservations", headers=headers, json=payload)
    response_json = response.json()

    response = requests.delete(f"{BASE_URL}/reservations/{response_json['id']}", headers=headers, json=payload)
    assert response.status_code == 200

def test_update_reservation(headers: dict) -> None:
    vehicle_payload = {
        "license_plate": generate_code(),
        "brand": "Toyota",
        "model": "Corolla",
        "color": "Red"
    }
    vehicle_response = requests.post(f"{BASE_URL}/vehicles", headers=headers, json=vehicle_payload)
    vehicle_json = vehicle_response.json()
    vehicle_id = vehicle_json["vehicle_id"]

    payload = {
        "vehicles_id": vehicle_id,
        "parking_lots_id": 1,
        "start_time": "2020-05-17 00:00:00",
        "end_time": "2020-05-17 12:00:00",
        "status": "confirmed",
        "cost": 10
    }
    response = requests.post(f"{BASE_URL}/reservations", headers=headers, json=payload)
    response_json = response.json()

    payload = {
        "vehicles_id": vehicle_id,
        "parking_lots_id": 1,
        "start_time": "2020-05-17 00:00:00",
        "end_time": "2020-05-17 12:00:00",
        "status": "confirmed",
        "cost": 11
    }
    reservation_id = response_json["id"]
    response = requests.put(f"{BASE_URL}/reservations/{reservation_id}", headers=headers, json=payload)

    assert response.status_code == 200

# sad flow
def test_get_non_existing_reservation(headers: dict) -> None:
    response = requests.get(f"{BASE_URL}/reservations/9999", headers=headers)
    assert response.status_code == 404
    
def test_non_existing_vehicle(headers: dict) -> None:
    payload = {
        "vehicles_id" : 9999,
        "parking_lots_id": 1,
        "start_time": "2020-05-17 00:00:00",
        "end_time" : "2020-05-17 12:00:00",
        "status": "confirmed",
        "cost": 10
    }
    response = requests.post(f"{BASE_URL}/reservations", headers=headers, json=payload)
    assert response.status_code == 403

def test_delete_non_existing(headers: dict) -> None:
    response = requests.delete(f"{BASE_URL}/reservations/9999", headers=headers)
    assert response.status_code == 404

def test__update_non_existing_reservation(headers: dict) -> None:
    payload = {
        "vehicles_id": 1,
        "parking_lots_id": 1,
        "start_time": "2020-05-17 00:00:00",
        "end_time": "2020-05-17 12:00:00",
        "status": "confirmed",
        "cost": 11
    }
    response = requests.put(f"{BASE_URL}/reservations/9999", headers=headers)
    assert response.status_code >= 400

def test__update_reservation_validation(headers: dict) -> None:
    vehicle_payload = {
        "license_plate": generate_code(),
        "brand": "Toyota",
        "model": "Corolla",
        "color": "Red"
    }
    vehicle_response = requests.post(f"{BASE_URL}/vehicles", headers=headers, json=vehicle_payload)
    vehicle_json = vehicle_response.json()
    vehicle_id = vehicle_json["vehicle_id"]

    payload = {
        "vehicles_id": vehicle_id,
        "parking_lots_id": 1,
        "start_time": "2020-05-17 00:00:00",
        "end_time": "2020-05-17 12:00:00",
        "status": "confirmed",
        "cost": 10
    }
    response = requests.post(f"{BASE_URL}/reservations", headers=headers, json=payload)
    response_json = response.json()

    payload = {
        "vehicles_id": vehicle_id,
        "parking_lots_id": -1,
        "start_time": "2020-d-17 00:00:00",
        "end_time": "2020-05-17 12:00:00",
        "status": "confirmed",
        "cost": 11
    }
    reservation_id = response_json["id"]
    response = requests.put(f"{BASE_URL}/reservations/{reservation_id}", headers=headers, json=payload)

    assert response.status_code >= 400

def generate_code() -> str:
    letters = ''.join(random.choices(string.ascii_uppercase, k=3))
    numbers = ''.join(random.choices(string.digits, k=3))
    return letters + numbers