from utils.errors import NotFoundError, ValidationError

NOTIFICATION_PREFS = ("email", "sms", "none")

USERS: dict[int, dict] = {
    1: {"id": 1, "name": "Alice", "email": "alice@example.com", "notification_pref": "none"},
    2: {"id": 2, "name": "Bob",   "email": "bob@example.com",   "notification_pref": "none"},
}

def get_user(user_id: int) -> dict:
    """Retrieve a user by ID.

    Args:
        user_id: The unique identifier for the user.

    Returns:
        The user record as a dictionary.

    Raises:
        NotFoundError: If no user exists with the given ID.
    """
    if user_id not in USERS:
        raise NotFoundError("User")
    return USERS[user_id]

def create_user(name: str, email: str) -> dict:
    """Create a new user.

    Args:
        name: The user's display name.
        email: The user's email address.

    Returns:
        The newly created user record.

    Raises:
        ValidationError: If name or email is empty.
    """
    if not name or not name.strip():
        raise ValidationError("name", "cannot be empty")
    if not email or "@" not in email:
        raise ValidationError("email", "must be a valid email address")
    new_id = max(USERS.keys()) + 1
    USERS[new_id] = {
        "id": new_id,
        "name": name,
        "email": email,
        "notification_pref": "none",
    }
    return USERS[new_id]

def list_users() -> list[dict]:
    """Retrieve all users.

    Returns:
        A list of every user record.
    """
    return list(USERS.values())

def get_notification_pref(user_id: int) -> dict:
    """Retrieve a user's notification preference.

    Args:
        user_id: The unique identifier for the user.

    Returns:
        A dictionary with the user's ID and notification preference.

    Raises:
        NotFoundError: If no user exists with the given ID.
    """
    if user_id not in USERS:
        raise NotFoundError("User")
    return {"user_id": user_id, "notification_pref": USERS[user_id]["notification_pref"]}

def update_notification_pref(user_id: int, pref: str) -> dict:
    """Update a user's notification preference.

    Args:
        user_id: The unique identifier for the user.
        pref: The new preference; must be one of NOTIFICATION_PREFS.

    Returns:
        A dictionary with the user's ID and updated notification preference.

    Raises:
        NotFoundError: If no user exists with the given ID.
        ValidationError: If pref is not one of NOTIFICATION_PREFS.
    """
    if user_id not in USERS:
        raise NotFoundError("User")
    if not isinstance(pref, str) or pref not in NOTIFICATION_PREFS:
        raise ValidationError(
            "notification_pref", f"must be one of: {', '.join(NOTIFICATION_PREFS)}"
        )
    USERS[user_id]["notification_pref"] = pref
    return {"user_id": user_id, "notification_pref": pref}
