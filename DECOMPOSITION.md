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
| SA-1 | 54 passed | `services/users.py` only | No |
| SA-2 | 54 passed (no new tests by design; tests are SA-4's job) | `services/users.py` only | No |
| SA-3 | 54 passed (no new tests by design) | `routes/api.py` only | No |
| SA-4 | 74 passed (20 new) | `tests/test_users.py` (new) only | No; no test failed, so there was nothing to report |

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

**Did Claude follow the constraint field for every subagent?**

Mostly, yes. After each subagent I checked which files had changed. Every subagent changed only its own Output file. The exceptions and near misses:

- **SA-2 and the CLAUDE.md test rule.** CLAUDE.md says "Every new service function gets a test in tests/test_tasks.py." SA-2 added three service functions and no tests, because the SA-2 prompt explicitly told it to skip that rule for this session. An explicit instruction in the prompt overrode a standing CLAUDE.md rule. That is what I wanted here, but it also means any prompt can override CLAUDE.md.
- **SA-3 nearly broke "no validation or if-statements in routes."** The PATCH route reads `data = request.get_json(silent=True) or {}` and then `data.get("notification_pref")`. Without the `or {}`, a missing body makes `None.get(...)` crash with a 500. Claude explained this and called it a default, not validation. It is still logic in routes/api.py that my constraint did not allow for.
- **SA-3 broke "Only add the new names to the existing services.users import."** It added the three names, but also reformatted the one-line `from services.users import get_user` into a multi-line block.
- **How the files were edited.** SA-2 appended its functions with a shell heredoc (`cat >> services/users.py <<'EOF'`). SA-3 rewrote the whole of routes/api.py with a Python script; the tool reported "+57 −39" even though only the import and three routes actually changed. Neither used Claude's normal Edit tool. I confirmed the existing routes were unchanged, but a full-file rewrite could have silently broken routes that SA-3 was told not to touch.

**Did any subagent's output break the next subagent's assumption? How did you recover?**

Yes, at the SA-2 → SA-3 hand-off. SA-2's hand-off was `update_notification_pref(user_id: int, pref: str)`, which expects a value already taken out of the request. SA-3 was told to do no validation, so it had to take the value out of the JSON body itself. That caused two problems:

1. A **missing body** returns `None`. SA-3 recovered within the same session by adding `or {}`, so the service receives `None` and returns 422.
2. A **body that is valid JSON but not an object**, e.g. `["sms"]` or `"sms"`, makes `get_json()` return a list or string with no `.get()`. That is still an unhandled 500 instead of a 422. **SA-4 did not catch it**: its prompt listed bad *values* (`"push"`, `""`, `"EMAIL"`, `None`, `5`) but not bad *body shapes*, so all 74 tests pass while the crash remains. Under my decomposition, nobody owned "is the body a JSON object?": SA-2 only saw the value, and SA-3 was told not to validate.

**Would you write the decomposition differently a second time? What would you change?**

- **Change SA-2's hand-off so the service takes the whole body**, the way `update_task(task_id, updates: dict)` already does in services/tasks.py: `update_notification_pref(user_id: int, body: dict | None)`. Then SA-2 owns all validation (missing body, non-object body, missing key, bad value), and SA-3's route is a true one-liner with no `or {}`.
- **Add body-shape cases to SA-4's prompt:** no body, `[]`, `"sms"`, and `{}` should each return 422.
- **Add "edit with the Edit tool only; do not rewrite whole files or write files from shell commands"** to every subagent's constraint, and **"do not reformat existing import lines"** to SA-3 and SA-4.
- **Fix CLAUDE.md's test rule** ("every new service function gets a test in tests/test_tasks.py") before starting. It points at the wrong file for user code, and it directly conflicts with a "tests come in a later subagent" pipeline.
