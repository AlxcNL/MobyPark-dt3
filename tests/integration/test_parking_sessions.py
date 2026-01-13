import requests
import pytest
import uuid

BASE_URL = "http://localhost:8000/v2"

# Shared state to store IDs across tests
@pytest.fixture(scope="module")
def test_data():
    return {"parking_lot_id": None, "vehicle_id": None, "session_id": None}

# happy flow
def test_01_start_parking_session(headers: dict, test_data: dict) -> None:
    unique_id = str(uuid.uuid4())[:6].upper()

    # Create parking lot
    payload = {
        "name": f"Test Parking {unique_id}",
        "location": "Downtown",
        "address": "123 Main Street, Cityville",
        "capacity": 150,
        "reserved": 20,
        "tariff": 2.5,
        "daytariff": 20.0,
        "latitude": 40.785091,
        "longitude": -73.968285,
    }
    response = requests.post(f"{BASE_URL}/parking-lots", headers=headers, json=payload)
    # Note: parking-lots endpoint returns Message, not the created object

    # Get the parking lots to find the ID we just created
    response = requests.get(f"{BASE_URL}/parking-lots", headers=headers)
    parking_lots = response.json()
    if parking_lots.get('items'):
        test_data["parking_lot_id"] = parking_lots['items'][-1]['id']  # Get last created

    # Create vehicle
    payload = {
        "license_plate": f"TST{unique_id}",
        "brand": "Toyota",
        "model": "Corolla",
        "color": "Red",
        "vehicle_name": "Test Car"
    }
    response = requests.post(f"{BASE_URL}/vehicles", headers=headers, json=payload)
    vehicle_data = response.json()
    test_data["vehicle_id"] = vehicle_data["vehicle_id"]

    # Start parking session
    parking_lot_id = test_data["parking_lot_id"]
    vehicle_id = test_data["vehicle_id"]
    license_plate = f"TST{unique_id}"

    payload = {
        "parking_lots_id": parking_lot_id,
        "vehicle_id": vehicle_id,
        "license_plate": license_plate
    }
    response = requests.post(f"{BASE_URL}/parking-lots/{parking_lot_id}/sessions/start", headers=headers, json=payload)
    assert response.status_code == 201
    session_data = response.json()
    test_data["session_id"] = session_data.get("id")

def test_02_get_all_sessions(headers: dict, test_data: dict) -> None:
    parking_lot_id = test_data["parking_lot_id"]
    response = requests.get(f"{BASE_URL}/parking-lots/{parking_lot_id}/sessions", headers=headers)
    assert response.status_code == 200

def test_03_get_parking_session(headers: dict, test_data: dict) -> None:
    parking_lot_id = test_data["parking_lot_id"]
    session_id = test_data["session_id"]
    response = requests.get(f"{BASE_URL}/parking-lots/{parking_lot_id}/sessions/{session_id}", headers=headers)
    assert response.status_code == 200

def test_04_delete_session(headers: dict, test_data: dict) -> None:
    parking_lot_id = test_data["parking_lot_id"]
    session_id = test_data["session_id"]
    response = requests.delete(f"{BASE_URL}/parking-lots/{parking_lot_id}/sessions/{session_id}", headers=headers)
    assert response.status_code == 200
    
# sad flow
def test_start_non_existing_parking_lot(headers: dict) -> None:
    payload = {
        "parking_lots_id": 9999,
        "vehicle_id": 9999,
        "license_plate": "FAKE999"
    }
    response = requests.post(f"{BASE_URL}/parking-lots/9999/sessions/start", headers=headers, json=payload)
    assert response.status_code == 404
    
def test_delete_non_existing_session(headers: dict) -> None:
    response = requests.delete(f"{BASE_URL}/parking-lots/1/sessions/9999", headers=headers)
    assert response.status_code >= 400

def test_update_non_existing_session(headers: dict) -> None:
    payload = {
        "parking_lots_id": 9999,
        "vehicle_id": 9999,
        "license_plate": "FAKE999"
    }
    response = requests.put(f"{BASE_URL}/parking-lots/9999/sessions/1", headers=headers, json=payload)
    assert response.status_code == 405

def test_stop_non_existing_session(headers: dict) -> None:
    response = requests.post(f"{BASE_URL}/parking-lots/9999/sessions/9999/stop", headers=headers)
    assert response.status_code == 404
    
    