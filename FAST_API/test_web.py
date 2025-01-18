import pytest


@pytest.mark.asyncio
async def test_add_recipe(client):
    recipe = {
        "title": "jhon2",
        "time": 2.2,
        "ingredients": "dfbsdhjjndkjf",
        "description": "dsjnfjkdsgngj",
        "views": 0,
    }
    resp = await client.post("/recipes", json=recipe)
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_get_recipes(client):
    resp = await client.get("/recipes")
    assert resp.status_code == 200
    response = resp.json()
    assert len(response) == 2


@pytest.mark.asyncio
async def test_get_recipes_by_id(client):
    resp = await client.get("/recipes/1")
    assert resp.status_code == 200
