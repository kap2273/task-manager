import pytest

from app import app
from services.users import (
    USERS,
    create_user,
    get_notification_pref,
    get_user,
    list_users,
    update_notification_pref,
)
from utils.errors import NotFoundError, ValidationError

PREF_ERROR = "Invalid notification_pref: must be one of: email, sms, none"


def test_list_users_returns_all():
    result = list_users()
    assert [user["id"] for user in result] == list(USERS.keys())
    assert all("notification_pref" in user for user in result)

def test_list_users_includes_new_user():
    user = create_user("Carol", "carol@example.com")
    assert user in list_users()

def test_seeded_users_default_to_none():
    assert get_user(1)["notification_pref"] == "none"
    assert get_user(2)["notification_pref"] == "none"

def test_create_user_defaults_to_none():
    user = create_user("Carol", "carol@example.com")
    assert user["notification_pref"] == "none"
    assert get_notification_pref(user["id"]) == {
        "user_id": user["id"], "notification_pref": "none"
    }

def test_get_notification_pref_valid():
    assert get_notification_pref(1) == {"user_id": 1, "notification_pref": "none"}

def test_get_notification_pref_unknown_user_raises_not_found():
    with pytest.raises(NotFoundError) as exc_info:
        get_notification_pref(999)
    assert exc_info.value.status_code == 404
    assert exc_info.value.message == "User not found"

@pytest.mark.parametrize("pref", ["email", "sms", "none"])
def test_update_notification_pref_valid(pref):
    user = create_user("Carol", "carol@example.com")
    result = update_notification_pref(user["id"], pref)
    assert result == {"user_id": user["id"], "notification_pref": pref}
    assert get_user(user["id"])["notification_pref"] == pref
    assert get_notification_pref(user["id"]) == result

def test_update_notification_pref_unknown_user_raises_not_found():
    with pytest.raises(NotFoundError) as exc_info:
        update_notification_pref(999, "email")
    assert exc_info.value.status_code == 404
    assert exc_info.value.message == "User not found"

@pytest.mark.parametrize("pref", ["push", "", "EMAIL", None, 5])
def test_update_notification_pref_invalid_raises_validation_error(pref):
    user = create_user("Carol", "carol@example.com")
    with pytest.raises(ValidationError) as exc_info:
        update_notification_pref(user["id"], pref)
    assert exc_info.value.status_code == 422
    assert exc_info.value.message == PREF_ERROR

def test_update_notification_pref_invalid_leaves_pref_unchanged():
    user = create_user("Carol", "carol@example.com")
    update_notification_pref(user["id"], "sms")
    with pytest.raises(ValidationError):
        update_notification_pref(user["id"], "push")
    assert get_user(user["id"])["notification_pref"] == "sms"

def test_list_users_route():
    client = app.test_client()
    user = create_user("Carol", "carol@example.com")
    ok = client.get("/api/users")
    assert ok.status_code == 200
    body = ok.get_json()
    assert all("notification_pref" in u for u in body)
    assert user in body

def test_get_user_route():
    client = app.test_client()
    ok = client.get("/api/users/1")
    assert ok.status_code == 200
    assert ok.get_json()["notification_pref"] == "none"
    missing = client.get("/api/users/999")
    assert missing.status_code == 404
    assert missing.get_json() == {"error": "User not found"}

def test_get_notification_pref_route():
    client = app.test_client()
    user = create_user("Carol", "carol@example.com")
    ok = client.get(f"/api/users/{user['id']}/notifications")
    assert ok.status_code == 200
    assert ok.get_json() == {"user_id": user["id"], "notification_pref": "none"}
    missing = client.get("/api/users/999/notifications")
    assert missing.status_code == 404
    assert missing.get_json() == {"error": "User not found"}

def test_update_notification_pref_route():
    client = app.test_client()
    user = create_user("Carol", "carol@example.com")
    url = f"/api/users/{user['id']}/notifications"
    ok = client.patch(url, json={"notification_pref": "email"})
    assert ok.status_code == 200
    assert ok.get_json() == {"user_id": user["id"], "notification_pref": "email"}
    assert client.get(url).get_json()["notification_pref"] == "email"
    assert client.get(f"/api/users/{user['id']}").get_json()["notification_pref"] == "email"
    missing = client.patch("/api/users/999/notifications", json={"notification_pref": "sms"})
    assert missing.status_code == 404
    assert missing.get_json() == {"error": "User not found"}
    bad = client.patch(url, json={"notification_pref": "push"})
    assert bad.status_code == 422
    assert bad.get_json() == {"error": PREF_ERROR}
    no_field = client.patch(url, json={})
    assert no_field.status_code == 422
    assert no_field.get_json() == {"error": PREF_ERROR}
    no_body = client.patch(url)
    assert no_body.status_code == 422
    assert no_body.get_json() == {"error": PREF_ERROR}
    assert client.get(url).get_json()["notification_pref"] == "email"
