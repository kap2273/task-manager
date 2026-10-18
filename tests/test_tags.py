from app import app


def test_create_tag_route():
    client = app.test_client()
    response = client.post("/api/tags", json={"name": "urgent"})
    assert response.status_code == 201
    assert response.get_json()["name"] == "urgent"
