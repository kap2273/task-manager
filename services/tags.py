from schemas.tags import ALLOWED_FIELDS, REQUIRED_FIELDS
from utils.errors import ValidationError

TAGS: dict[int, dict] = {}

def create_tag(data: dict | None) -> dict:
    """Create a new tag.

    Args:
        data: The parsed JSON request body. Must contain a non-empty "name".

    Returns:
        The newly created tag record.

    Raises:
        ValidationError: If data is not a dict, is missing a required field,
            contains a field that is not allowed, or has an empty name.
    """
    if not isinstance(data, dict):
        raise ValidationError("body", "must be a JSON object")
    for field in REQUIRED_FIELDS:
        if field not in data:
            raise ValidationError(field, "is required")
    for field in data:
        if field not in ALLOWED_FIELDS:
            raise ValidationError(field, "is not allowed")
    name = data["name"]
    if not isinstance(name, str) or not name.strip():
        raise ValidationError("name", "cannot be empty")
    new_id = max(TAGS.keys(), default=0) + 1
    TAGS[new_id] = {"id": new_id, "name": name}
    return TAGS[new_id]
