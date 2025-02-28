import pytest
import os


def test_add_twit_with_file(client):
    path_test_file = os.path.join(os.path.dirname(__file__), "test_file")
    files = {
        "file": [
            open(os.path.join(path_test_file, "IMG_7960.MP4"), "rb"),
            open(os.path.join(path_test_file, "Pasted image.png"), "rb"),
        ]
    }
    headers = {"api-key": "12345"}
    response = client.post("/api/medias", headers=headers, data=files)
    assert response.status_code == 201
    data = {"tweet_data": "some text 2", "tweet_media_ids": [1, 2]}
    response = client.post("/api/tweets", headers=headers, json=data)
    assert response.status_code == 201


def test_delete_twit(client):
    headers = {"api-key": "12345"}
    response = client.delete("/api/tweets/1", headers=headers)
    assert response.status_code == 200


def test_get_twits(client):
    headers = {"api-key": "12345"}
    response = client.get("/api/tweets", headers=headers)
    assert response.status_code == 200
    data = response.get_json()
    assert len(data["tweets"]) == 1
