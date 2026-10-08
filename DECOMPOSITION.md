# DECOMPOSITION — Task 2: Notification preferences

## Feature
A user has a `notification_pref`: `"email"`, `"sms"`, or `"none"` (default `"none"`).
- `PATCH /api/users/<id>/notifications` updates it; invalid values → `ValidationError` (422)
- `GET /api/users/<id>/notifications` returns it
- User detail (`GET /api/users/<id>`) and user list (`GET /api/users`) include it

## Notes on this codebase
- There is no `models/` layer or database. The "User model" is the `USERS` dict in
  `services/users.py`, so the data layer and service layer live in the same file.
  SA-1 and SA-2 are separated by *what* they may change in that file, not by file.
- There is no user list endpoint yet. SA-2 adds `list_users` and SA-3 adds
  `GET /api/users` so the "user list includes notification_pref" requirement can be met.
- "Nullable column" → the key `notification_pref` is on every user record, with
  `"none"` as the stored default.

## Subagent table

| Subagent # | Input | Task | Output | Constraint | Hand-off |
|---|---|---|---|---|---|
| **SA-1: Data layer** | `CLAUDE.md`, `services/users.py` | Add the `notification_pref` field to every user record (seed data and `create_user`) with default `"none"`, plus a constant listing the allowed values. | `services/users.py` | Only edit the `USERS` seed dict, the record built inside `create_user`, and add one module constant. Do not add new functions. Do not change `create_user`'s signature. Do not touch `routes/api.py`, `services/tasks.py`, or anything in `tests/`. | Key name `"notification_pref"`; default `"none"`; constant `NOTIFICATION_PREFS = ("email", "sms", "none")` in `services/users.py` |
| **SA-2: Service layer** | `CLAUDE.md`, `services/users.py`, `utils/errors.py` | Add `list_users`, `get_notification_pref`, and `update_notification_pref` service functions that validate input and raise `AppError` subclasses. | `services/users.py` | Only add new functions. Do not modify `USERS`, `NOTIFICATION_PREFS`, `get_user`, or `create_user`. Do not touch `routes/api.py` or anything in `tests/` (tests are SA-4's job, even though CLAUDE.md says every new service function gets a test). | Signatures: `list_users() -> list[dict]`; `get_notification_pref(user_id: int) -> dict`; `update_notification_pref(user_id: int, pref: str) -> dict`. Both pref functions return `{"user_id": <id>, "notification_pref": <value>}`. Errors: `NotFoundError("User")`, `ValidationError("notification_pref", "must be one of: email, sms, none")` |
| **SA-3: API layer** | `CLAUDE.md`, `routes/api.py`, `services/users.py` (read only) | Add `GET /api/users`, `GET /api/users/<id>/notifications`, and `PATCH /api/users/<id>/notifications` routes that each call one service function. | `routes/api.py` | Only edit `routes/api.py`. Do not edit anything in `services/`, `utils/`, or `tests/`. No validation or logic in routes; pass the raw JSON value through. Do not change existing routes or URLs. Only add the new names to the existing `services.users` import. | URLs + request/response shapes: PATCH body `{"notification_pref": "email"}` → 200 with `{"user_id", "notification_pref"}`; bad value → 422 `{"error": ...}`; unknown user → 404 |
| **SA-4: Tests** | `CLAUDE.md`, `services/users.py`, `routes/api.py`, `tests/test_tasks.py` (for style only) | Write tests for the three service functions and the three new routes, including that user detail and list include `notification_pref`. | `tests/test_users.py` (new) | Only create `tests/test_users.py`. Do not edit any file in `services/`, `routes/`, `utils/`, or `tests/test_tasks.py`. If a test fails because of a bug in the code, stop and report it instead of fixing the code. | Final: `python -m pytest -q` green |

## Results (fill in after each subagent)

| Subagent | `python -m pytest -q` result | Files actually changed (`git diff --stat`) | Fix needed in same session? |
|---|---|---|---|
| SA-1 | | | |
| SA-2 | | | |
| SA-3 | | | |
| SA-4 | | | |

## Exact prompts

Run each one in a fresh session: `/clear` before pasting. Commit after each one.

### SA-1 prompt
```
You are SA-1 (data layer) for a notification-preference feature.
Read: CLAUDE.md, services/users.py.

Task: Add a "notification_pref" field to every user record in services/users.py.
- Add a module constant NOTIFICATION_PREFS = ("email", "sms", "none")
- Add "notification_pref": "none" to each user in the USERS seed dict
- New users created by create_user also get "notification_pref": "none"

Constraints:
- Only edit services/users.py: the USERS dict, the record built in create_user, and the new constant.
- Do not add any new functions. Do not change create_user's signature.
- Do not touch routes/api.py, services/tasks.py, or anything in tests/.

Verification: python -m pytest -q passes.
```

### SA-2 prompt
```
You are SA-2 (service layer) for a notification-preference feature.
Read: CLAUDE.md, services/users.py, utils/errors.py.
SA-1 already added NOTIFICATION_PREFS and a "notification_pref" key (default "none") on every user.

Task: Add three new functions to services/users.py, following the get_user pattern
(type hints, Google-style docstrings, AppError subclasses):
- list_users() -> list[dict]: all user records
- get_notification_pref(user_id: int) -> dict: returns {"user_id": id, "notification_pref": value}
- update_notification_pref(user_id: int, pref: str) -> dict: validates and saves, returns the same shape
  - unknown user -> NotFoundError("User")
  - pref not in NOTIFICATION_PREFS (including non-strings, None, "EMAIL") ->
    ValidationError("notification_pref", "must be one of: email, sms, none")

Constraints:
- Only add new functions to services/users.py.
- Do not modify USERS, NOTIFICATION_PREFS, get_user, or create_user.
- Do not touch routes/api.py or anything in tests/. Tests are written by a later subagent,
  so skip CLAUDE.md's "every new service function gets a test" rule for this session.

Verification: python -m pytest -q passes.
```

### SA-3 prompt
```
You are SA-3 (API layer) for a notification-preference feature.
Read: CLAUDE.md, routes/api.py, services/users.py (read only).
services/users.py already has list_users(), get_notification_pref(user_id),
and update_notification_pref(user_id, pref), which validate and raise AppError subclasses.

Task: Add three routes to routes/api.py:
- GET   /api/users                          -> list_users()
- GET   /api/users/<int:user_id>/notifications -> get_notification_pref(user_id)
- PATCH /api/users/<int:user_id>/notifications -> update_notification_pref(user_id, <value of "notification_pref" from the JSON body>)
  Use request.get_json(silent=True) so a missing body still reaches the service.

Constraints:
- Only edit routes/api.py. Do not edit anything in services/, utils/, or tests/.
- Routes are HTTP only: one service call each, no validation or if-statements on the value.
- Do not change existing routes or URLs. Only add the new names to the existing services.users import.

Verification: python -m pytest -q passes.
```

### SA-4 prompt
```
You are SA-4 (tests) for a notification-preference feature.
Read: CLAUDE.md, services/users.py, routes/api.py, tests/test_tasks.py (for style only).

Task: Create tests/test_users.py covering:
- list_users, get_notification_pref, update_notification_pref (valid values, unknown user -> 404,
  invalid values "push", "", "EMAIL", None, 5 -> 422 with exact message)
- Seed users and newly created users default to "none"
- Routes via app.test_client(): GET /api/users and GET /api/users/<id> include notification_pref;
  GET and PATCH /api/users/<id>/notifications return 200 / 404 / 422 with {"error": ...}

Constraints:
- Only create tests/test_users.py. Do not edit services/, routes/, utils/, or tests/test_tasks.py.
- USERS is shared across tests: a test that changes a preference should use a user it created,
  and must not assert exact list lengths.
- If a test fails because of a bug in the code, stop and tell me. Do not fix the code yourself.

Verification: python -m pytest -q passes.
```

## Divergence

<!-- Fill in after all four subagents have run. -->

**Did Claude follow the constraint field for every subagent?**

**Did any subagent's output break the next subagent's assumption? How did you recover?**

**Would you write the decomposition differently a second time? What would you change?**
