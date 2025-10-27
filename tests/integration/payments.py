import requests

BASE_URL = "http://localhost:8000"

#happy flow
def test_get_payments(headers: dict) -> None:
    response = requests.get(f"{BASE_URL}/payments", headers=headers)
    assert response.status_code == 200

def test_get_payment_by_user_id(headers: dict) -> None:
    response = requests.get(f"{BASE_URL}/payments/1", headers=headers)
    assert response.status_code == 200

def test_make_payment(headers: dict) -> None:
    #make the payment
    payload_payment = {
      "sessions_id": 2, # make sure session exists
      "method": "card",
      "issuer": "Visa",
      "bank": "TestBank"
    }
    response = requests.post(f"{BASE_URL}/payments", headers=headers, json=payload_payment)
    assert response.status_code == 200

    #finish the payment
    json = response.json()
    payment_id = json["id"]
    response = requests.post(f"{BASE_URL}/payments/{payment_id}", headers=headers, json=payload_payment)
    assert response.status_code == 200

#sad flow
def test_get_payment_non_existing_user_id(headers: dict) -> None:
    response = requests.get(f"{BASE_URL}/payments/9999", headers=headers)
    assert response.status_code == 404

def test_non_make_payment_non_existing_id(headers: dict) -> None:
    payload_payment = {
        "sessions_id": 9999,
        "method": "card",
        "issuer": "Visa",
        "bank": "TestBank"
    }
    response = requests.post(f"{BASE_URL}/payments", headers=headers, json=payload_payment)
    assert response.status_code == 404

def test_non_make_payment_validation(headers: dict) -> None:
    payload_payment = {
        "sessions_id": -9999,
        "method": 22,
        "issuer": "Visa",
        "bank": "TestBank"
    }
    response = requests.post(f"{BASE_URL}/payments", headers=headers, json=payload_payment)
    assert response.status_code >= 400