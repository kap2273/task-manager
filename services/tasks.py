from services.users import USERS
from utils.errors import NotFoundError, ValidationError

DEFAULT_PRIORITY = 3
MIN_PRIORITY = 1
MAX_PRIORITY = 5
SORT_FIELDS = ("priority",)

TASKS: dict[int, dict] = {
    1: {"id": 1, "title": "Buy groceries",  "done": False, "user_id": 1, "priority": 3},
    2: {"id": 2, "title": "Write report",   "done": False, "user_id": 1, "priority": 3},
    3: {"id": 3, "title": "Call dentist",   "done": True,  "user_id": 2, "priority": 3},
}

def process_order(task_id: int) -> dict:
    """Mark a task as done.

    Args:
        task_id: The unique identifier for the task.

    Returns:
        The updated task record.

    Raises:
        NotFoundError: If no task exists with the given ID.
    """
    if task_id not in TASKS:
        raise NotFoundError("Task")
    task = TASKS[task_id]
    task["done"] = True
    return task

def get_task(task_id: int) -> dict:
    """Retrieve a task by ID.

    Args:
        task_id: The unique identifier for the task.

    Returns:
        The task record as a dictionary.

    Raises:
        NotFoundError: If no task exists with the given ID.
    """
    if task_id not in TASKS:
        raise NotFoundError("Task")
    return TASKS[task_id]

def _validate_priority(priority: int) -> None:
    """Check that a priority is an integer from 1 to 5.

    Args:
        priority: The priority to check. 1 is the most urgent.

    Raises:
        ValidationError: If priority is not an int (bools included) or is out of range.
    """
    if isinstance(priority, bool) or not isinstance(priority, int):
        raise ValidationError("priority", "must be an integer")
    if not MIN_PRIORITY <= priority <= MAX_PRIORITY:
        raise ValidationError(
            "priority", f"must be between {MIN_PRIORITY} and {MAX_PRIORITY}"
        )

def create_task(title: str, user_id: int, priority: int = DEFAULT_PRIORITY) -> dict:
    """Create a new task.

    Args:
        title: The task's title.
        user_id: The unique identifier for the user who owns the task.
        priority: Urgency from 1 (most urgent) to 5. Defaults to 3.

    Returns:
        The newly created task record.

    Raises:
        ValidationError: If title is not a non-empty string, user_id is not an
            int, or priority is invalid.
        NotFoundError: If no user exists with the given ID.
    """
    if not isinstance(title, str) or not title.strip():
        raise ValidationError("title", "cannot be empty")
    if isinstance(user_id, bool) or not isinstance(user_id, int):
        raise ValidationError("user_id", "must be an integer")
    if user_id not in USERS:
        raise NotFoundError("User")
    _validate_priority(priority)
    new_id = max(TASKS.keys()) + 1
    TASKS[new_id] = {"id": new_id, "title": title,
                     "done": False, "user_id": user_id, "priority": priority}
    return TASKS[new_id]

def get_tasks_for_user(user_id: int) -> list[dict]:
    """Retrieve all tasks owned by a user.

    Args:
        user_id: The unique identifier for the user.

    Returns:
        A list of the user's task records. Empty if the user has no tasks.

    Raises:
        NotFoundError: If no user exists with the given ID.
    """
    if user_id not in USERS:
        raise NotFoundError("User")
    return [task for task in TASKS.values() if task["user_id"] == user_id]

def list_tasks(priority: str | None = None, sort: str | None = None) -> list[dict]:
    """Retrieve all tasks, optionally filtered by priority and sorted.

    Args:
        priority: Raw priority string from the query string, or None for all tasks.
        sort: Field to sort by, or None to keep insertion order. Only "priority"
            is supported; it orders tasks most urgent first (1 to 5), keeping
            insertion order among tasks with the same priority.

    Returns:
        A list of task records. Empty if no tasks match.

    Raises:
        ValidationError: If priority is not an integer string from 1 to 5, or
            sort is not a supported field.
    """
    if sort is not None and sort not in SORT_FIELDS:
        allowed = ", ".join(f"'{field}'" for field in SORT_FIELDS)
        raise ValidationError("sort", f"must be {allowed}")
    if priority is None:
        tasks = list(TASKS.values())
    else:
        digits = priority.removeprefix("-")
        if not (digits.isascii() and digits.isdigit()):
            raise ValidationError("priority", "must be an integer")
        priority_value = int(priority)
        _validate_priority(priority_value)
        tasks = [task for task in TASKS.values() if task["priority"] == priority_value]
    if sort == "priority":
        tasks = sorted(tasks, key=lambda task: task["priority"])
    return tasks

def update_task(task_id: int, updates: dict) -> dict:
    """Update a task's title, done flag, and/or priority.

    All fields are validated before any change is applied, so a failed
    update leaves the task untouched.

    Args:
        task_id: The unique identifier for the task.
        updates: Fields to change. Allowed keys: "title", "done", "priority".

    Returns:
        The full updated task record.

    Raises:
        NotFoundError: If no task exists with the given ID.
        ValidationError: If updates is not a dict, contains a field that cannot
            be updated, or contains an invalid value.
    """
    if task_id not in TASKS:
        raise NotFoundError("Task")
    if not isinstance(updates, dict):
        raise ValidationError("body", "must be a JSON object")
    for field in updates:
        if field not in ("title", "done", "priority"):
            raise ValidationError(field, "cannot be updated")
    if "title" in updates:
        title = updates["title"]
        if not isinstance(title, str) or not title.strip():
            raise ValidationError("title", "cannot be empty")
    if "done" in updates and not isinstance(updates["done"], bool):
        raise ValidationError("done", "must be a boolean")
    if "priority" in updates:
        _validate_priority(updates["priority"])
    TASKS[task_id].update(updates)
    return TASKS[task_id]
