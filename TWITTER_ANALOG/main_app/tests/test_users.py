import pytest


def test_get_my_info(client):
    headers = {"api-key": "12345"}
    response = client.get("/api/users/me", headers=headers)
    data = response.get_json()
    assert response.status_code == 200
    assert data["user"]["id"] == 1


def test_get_user_info_by_id(client):
    headers = {"api-key": "12345"}
    response = client.get("/api/users/2", headers=headers)
    assert response.status_code == 200
    data = response.get_json()
    assert data["user"]["id"] == 2
