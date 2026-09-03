def test_health_check(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_root(client):
    response = client.get("/")
    assert response.status_code == 200


def test_moderate_flagged_text(client):
    response = client.post("/moderate", json={"text": "You are such an idiot"})
    assert response.status_code == 200
    data = response.json()
    assert data["is_flagged"] is True
    assert data["category"] == "abusive"
    assert "id" in data
    assert "created_at" in data


def test_moderate_clean_text(client):
    response = client.post("/moderate", json={"text": "Have a nice day"})
    assert response.status_code == 200
    data = response.json()
    assert data["is_flagged"] is False
    assert data["category"] == "clean"


def test_moderate_empty_text_rejected(client):
    response = client.post("/moderate", json={"text": ""})
    assert response.status_code == 422


def test_moderate_whitespace_only_text_rejected(client):
    response = client.post("/moderate", json={"text": "   "})
    assert response.status_code == 422


def test_moderate_missing_text_field(client):
    response = client.post("/moderate", json={})
    assert response.status_code == 422


def test_get_moderation_result_success(client):
    create_response = client.post("/moderate", json={"text": "Buy now, click here"})
    created_id = create_response.json()["id"]

    get_response = client.get(f"/moderation/{created_id}")
    assert get_response.status_code == 200
    data = get_response.json()
    assert data["id"] == created_id
    assert data["category"] == "spam"


def test_get_moderation_result_not_found(client):
    response = client.get("/moderation/99999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Moderation result not found"


def test_get_moderation_result_invalid_id_type(client):
    response = client.get("/moderation/not-a-number")
    assert response.status_code == 422