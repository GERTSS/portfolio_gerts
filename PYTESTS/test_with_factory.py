import pytest
from factories import ClientFactory, ParkingFactory


def test_create_client(db, client):
    client_data = ClientFactory.build()
    response = client.post(
        "/clients",
        json={
            "name": client_data.name,
            "surname": client_data.surname,
            "credit_card": client_data.credit_card,
            "car_number": client_data.car_number,
        },
    )
    assert response.status_code == 200


def test_create_parking(db, client):
    parking_data = ParkingFactory.build()
    response = client.post(
        "/parking",
        json={
            "address": parking_data.address,
            "opened": parking_data.opened,
            "count_places": parking_data.count_places,
            "count_available_places": parking_data.count_available_places,
        },
    )
    assert response.status_code == 200
