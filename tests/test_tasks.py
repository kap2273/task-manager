import pytest

from app import app
from services.tasks import (
    TASKS,
    create_task,
    get_task,
    get_tasks_for_user,
    list_tasks,
    process_order,
    update_task,
)
from utils.errors import NotFoundError, ValidationError


def test_process_order_valid():
    result = process_order(1)
    assert result["done"] is True

def test_process_order_invalid():
    with pytest.raises(Exception):
        process_order(999)

def test_get_task_valid():
    result = get_task(2)
    assert result["title"] == "Write report"

def test_get_task_invalid():
    with pytest.raises(Exception):
        get_task(999)

def test_get_task_invalid_raises_not_found():
    with pytest.raises(NotFoundError) as exc_info:
        get_task(999)
    assert exc_info.value.status_code == 404
    assert exc_info.value.message == "Task not found"

def test_create_task_valid():
    result = create_task("Plan trip", 1)
    assert result["title"] == "Plan trip"
    assert result["user_id"] == 1
    assert result["done"] is False
    assert get_task(result["id"]) == result

def test_create_task_empty_title_raises_validation_error():
    with pytest.raises(ValidationError) as exc_info:
        create_task("   ", 1)
    assert exc_info.value.status_code == 422
    assert exc_info.value.message == "Invalid title: cannot be empty"

def test_create_task_unknown_user_raises_not_found():
    with pytest.raises(NotFoundError) as exc_info:
        create_task("Plan trip", 999)
    assert exc_info.value.status_code == 404
    assert exc_info.value.message == "User not found"

def test_get_tasks_for_user_valid():
    result = get_tasks_for_user(2)
    assert all(task["user_id"] == 2 for task in result)
    assert 3 in [task["id"] for task in result]
    assert 1 not in [task["id"] for task in result]

def test_get_tasks_for_user_unknown_user_raises_not_found():
    with pytest.raises(NotFoundError) as exc_info:
        get_tasks_for_user(999)
    assert exc_info.value.status_code == 404
    assert exc_info.value.message == "User not found"

def test_seeded_tasks_have_priority():
    for task in TASKS.values():
        assert isinstance(task["priority"], int)
        assert 1 <= task["priority"] <= 5

def test_create_task_default_priority():
    result = create_task("Plan trip", 1)
    assert result["priority"] == 3

def test_create_task_with_priority():
    result = create_task("Pay rent", 1, 1)
    assert result["priority"] == 1
    assert get_task(result["id"])["priority"] == 1

@pytest.mark.parametrize("priority", [0, 6])
def test_create_task_priority_out_of_range_raises_validation_error(priority):
    with pytest.raises(ValidationError) as exc_info:
        create_task("Plan trip", 1, priority)
    assert exc_info.value.status_code == 422
    assert exc_info.value.message == "Invalid priority: must be between 1 and 5"

@pytest.mark.parametrize("priority", ["2", 2.0, None, True])
def test_create_task_priority_non_int_raises_validation_error(priority):
    with pytest.raises(ValidationError) as exc_info:
        create_task("Plan trip", 1, priority)
    assert exc_info.value.status_code == 422
    assert exc_info.value.message == "Invalid priority: must be an integer"

def test_create_task_route_priority():
    client = app.test_client()
    ok = client.post("/api/tasks", json={"title": "Plan trip", "user_id": 1, "priority": 2})
    assert ok.status_code == 201
    assert ok.get_json()["priority"] == 2
    default = client.post("/api/tasks", json={"title": "Plan trip", "user_id": 1})
    assert default.status_code == 201
    assert default.get_json()["priority"] == 3
    bad = client.post("/api/tasks", json={"title": "Plan trip", "user_id": 1, "priority": 9})
    assert bad.status_code == 422
    assert bad.get_json() == {"error": "Invalid priority: must be between 1 and 5"}

def test_update_task_valid():
    task = create_task("Plan trip", 1)
    result = update_task(task["id"], {"title": "Book flights", "done": True, "priority": 1})
    assert result["title"] == "Book flights"
    assert result["done"] is True
    assert result["priority"] == 1
    assert result["user_id"] == 1
    assert get_task(task["id"]) == result

def test_update_task_empty_updates_returns_unchanged():
    task = create_task("Plan trip", 1)
    before = dict(task)
    assert update_task(task["id"], {}) == before

def test_update_task_unknown_task_raises_not_found():
    with pytest.raises(NotFoundError) as exc_info:
        update_task(999, {"priority": 1})
    assert exc_info.value.status_code == 404
    assert exc_info.value.message == "Task not found"

@pytest.mark.parametrize("updates, message", [
    ({"priority": 6}, "Invalid priority: must be between 1 and 5"),
    ({"priority": True}, "Invalid priority: must be an integer"),
    ({"title": "  "}, "Invalid title: cannot be empty"),
    ({"title": 5}, "Invalid title: cannot be empty"),
    ({"done": "yes"}, "Invalid done: must be a boolean"),
    ({"user_id": 2}, "Invalid user_id: cannot be updated"),
    (None, "Invalid body: must be a JSON object"),
])
def test_update_task_invalid_raises_validation_error(updates, message):
    task = create_task("Plan trip", 1)
    with pytest.raises(ValidationError) as exc_info:
        update_task(task["id"], updates)
    assert exc_info.value.status_code == 422
    assert exc_info.value.message == message

def test_update_task_invalid_leaves_task_unchanged():
    task = create_task("Plan trip", 1)
    before = dict(task)
    with pytest.raises(ValidationError):
        update_task(task["id"], {"title": "New title", "priority": 0})
    assert get_task(task["id"]) == before

def test_update_task_route():
    client = app.test_client()
    task = create_task("Plan trip", 1)
    ok = client.patch(f"/api/tasks/{task['id']}", json={"priority": 5})
    assert ok.status_code == 200
    assert ok.get_json() == {**task, "priority": 5}
    missing = client.patch("/api/tasks/999", json={"priority": 5})
    assert missing.status_code == 404
    assert missing.get_json() == {"error": "Task not found"}
    bad = client.patch(f"/api/tasks/{task['id']}", json={"priority": 9})
    assert bad.status_code == 422
    assert bad.get_json() == {"error": "Invalid priority: must be between 1 and 5"}
    no_body = client.patch(f"/api/tasks/{task['id']}")
    assert no_body.status_code == 422

def test_list_tasks_no_filter_returns_all():
    result = list_tasks()
    assert [task["id"] for task in result] == list(TASKS.keys())

def test_list_tasks_filters_by_priority():
    urgent = create_task("Pay rent", 1, 1)
    later = create_task("Clean garage", 1, 5)
    result = list_tasks("1")
    ids = [task["id"] for task in result]
    assert urgent["id"] in ids
    assert later["id"] not in ids
    assert all(task["priority"] == 1 for task in result)

@pytest.mark.parametrize("priority", ["0", "6", "-1"])
def test_list_tasks_priority_out_of_range_raises_validation_error(priority):
    with pytest.raises(ValidationError) as exc_info:
        list_tasks(priority)
    assert exc_info.value.status_code == 422
    assert exc_info.value.message == "Invalid priority: must be between 1 and 5"

@pytest.mark.parametrize("priority", ["abc", "", "2.5", " 2", "+2", "--1", "²"])
def test_list_tasks_priority_non_int_raises_validation_error(priority):
    with pytest.raises(ValidationError) as exc_info:
        list_tasks(priority)
    assert exc_info.value.status_code == 422
    assert exc_info.value.message == "Invalid priority: must be an integer"

def test_list_tasks_route_priority():
    client = app.test_client()
    task = create_task("Plan trip", 1, 2)
    ok = client.get("/api/tasks?priority=2")
    assert ok.status_code == 200
    assert task["id"] in [t["id"] for t in ok.get_json()]
    assert all(t["priority"] == 2 for t in ok.get_json())
    unfiltered = client.get("/api/tasks")
    assert unfiltered.status_code == 200
    assert [t["id"] for t in unfiltered.get_json()] == list(TASKS.keys())
    out_of_range = client.get("/api/tasks?priority=9")
    assert out_of_range.status_code == 422
    assert out_of_range.get_json() == {"error": "Invalid priority: must be between 1 and 5"}
    non_int = client.get("/api/tasks?priority=abc")
    assert non_int.status_code == 422
    assert non_int.get_json() == {"error": "Invalid priority: must be an integer"}
    empty = client.get("/api/tasks?priority=")
    assert empty.status_code == 422

def test_list_tasks_sort_by_priority():
    low = create_task("Clean garage", 1, 5)
    urgent = create_task("Pay rent", 1, 1)
    mid = create_task("Plan trip", 1, 2)
    result = list_tasks(sort="priority")
    priorities = [task["priority"] for task in result]
    assert priorities == sorted(priorities)
    ids = [task["id"] for task in result]
    assert ids.index(urgent["id"]) < ids.index(mid["id"]) < ids.index(low["id"])

def test_list_tasks_sort_by_priority_is_stable():
    create_task("Pay rent", 1, 1)
    create_task("Pay bills", 1, 1)
    result = list_tasks(sort="priority")
    for level in range(1, 6):
        ids = [task["id"] for task in result if task["priority"] == level]
        assert ids == sorted(ids)

def test_list_tasks_sort_with_priority_filter():
    first = create_task("Pay rent", 1, 1)
    second = create_task("Pay bills", 1, 1)
    create_task("Clean garage", 1, 5)
    result = list_tasks("1", "priority")
    assert all(task["priority"] == 1 for task in result)
    ids = [task["id"] for task in result]
    assert ids == sorted(ids)
    assert first["id"] in ids and second["id"] in ids

def test_list_tasks_no_sort_keeps_insertion_order():
    create_task("Clean garage", 1, 5)
    create_task("Pay rent", 1, 1)
    result = list_tasks(sort=None)
    assert [task["id"] for task in result] == list(TASKS.keys())

@pytest.mark.parametrize("sort", ["", "title", "Priority", "-priority"])
def test_list_tasks_invalid_sort_raises_validation_error(sort):
    with pytest.raises(ValidationError) as exc_info:
        list_tasks(sort=sort)
    assert exc_info.value.status_code == 422
    assert exc_info.value.message == "Invalid sort: must be 'priority'"

def test_list_tasks_route_sort():
    client = app.test_client()
    create_task("Clean garage", 1, 5)
    create_task("Pay rent", 1, 1)
    task = create_task("Plan trip", 1, 2)
    ok = client.get("/api/tasks?sort=priority")
    assert ok.status_code == 200
    priorities = [t["priority"] for t in ok.get_json()]
    assert priorities == sorted(priorities)
    filtered = client.get("/api/tasks?priority=2&sort=priority")
    assert filtered.status_code == 200
    assert task["id"] in [t["id"] for t in filtered.get_json()]
    assert all(t["priority"] == 2 for t in filtered.get_json())
    bad_sort = client.get("/api/tasks?sort=bogus")
    assert bad_sort.status_code == 422
    assert bad_sort.get_json() == {"error": "Invalid sort: must be 'priority'"}
    bad_priority = client.get("/api/tasks?priority=9&sort=priority")
    assert bad_priority.status_code == 422
    assert bad_priority.get_json() == {"error": "Invalid priority: must be between 1 and 5"}
