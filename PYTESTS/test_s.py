import pytest


@pytest.mark.parametrize(
    "endpoint, params", [("/clients", None), ("/clients/<int:id>", {"id": 1})]
)
def test_get_methods(client, endpoint, params):
    if params:
        endpoint = endpoint.replace("<int:id>", str(params["id"]))
    response = client.get(endpoint)
    assert response.status_code == 200


def test_add_client(client):
    new_client = {
        "name": "jhon2",
        "surname": "jhonson2",
        "count_places": 100,
        "count_available_places": 100,
    }
    resp = client.post("/parkings", data=new_client)
    assert resp.status_code == 200


def test_add_parking(client):
    new_parking = {
        "address": "dhsfbhewbfhj",
        "opened": True,
        "credit_card": "487657454548",
        "car_number": "6ABC54",
    }
    resp = client.post("/clients", data=new_parking)
    assert resp.status_code == 200


@pytest.mark.parking
def test_add_booking(client, db):
    data = {"client_id": 1, "parking_id": 1}
    resp = client.post("/client_parkings", data=data)
    assert resp.status_code == 200
    parking = db.session.query(Parking).get(1)
    assert parking.count_available_places == 99


@pytest.mark.parking
def test_delete_booking(client, db):
    data = {"client_id": 1, "parking_id": 1}
    resp = client.delete("/client_parkings", data=data)
    assert resp.status_code == 200
    booking = (
        db.session.query(ClientParking)
        .filter_by(client_id=data["client_id"], parking_id=data["parking_id"])
        .first()
    )
    assert booking is None
