import requests

BASE_URL = "http://localhost:8000"

# happy flow
def test_get_all_reservations(headers):
    response = requests.get(f"{BASE_URL}/reservations", headers=headers)
    assert response.status_code == 200
    
# sad flow
def test_get_non_existing_reservation(headers):
    response = requests.get(f"{BASE_URL}/reservations", headers=headers)
    assert response.status_code == 404
    
    