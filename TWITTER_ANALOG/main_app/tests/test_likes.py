import pytest


def test_delete_like(client):
    headers = {"api-key": "12345"}
    response = client.delete("/api/tweets/1/likes", headers=headers)
    assert response.status_code == 200


def test_create_like(client):
    headers = {"api-key": "67890"}
    response = client.post("/api/tweets/1/likes", headers=headers)
    assert response.status_code == 200
