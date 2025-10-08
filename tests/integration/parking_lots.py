import requests

BASE_URL = "http://localhost:8000"

# happy flow
def test___get_all_parking_lots(headers):
    response = requests.get(f"{BASE_URL}/parking-lots", headers=headers)
    assert response.status_code == 200
# sad flow