import pytest


def test_delete_follow(client):
    headers = {"api-key": "12345"}
    response = client.delete("/api/users/2/follow", headers=headers)
    assert response.status_code == 200


def test_create_follow(client):
    headers = {"api-key": "67890"}
    response = client.post("/api/users/1/follow", headers=headers)
    assert response.status_code == 200
