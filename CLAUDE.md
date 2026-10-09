# Task Manager
Flask REST API for tasks and users. Data is stored in in-memory dicts (no database yet).

## Commands
Run everything from the task-manager/ root.
- Install: `pip install -r requirements.txt`
- Install linter (once): `pip install ruff`
- Run app: `python app.py` → endpoints live under http://127.0.0.1:5000/api/
- Run all tests: `pytest -v`
- Run one test: `pytest tests/test_tasks.py::test_get_task_invalid -v`
- Lint: `ruff check <files you changed>`
- Before finishing any task: `pytest -v` passes and `ruff check` is clean on changed files.
- `pytest` and `ruff` are not on PATH on this machine: use `python -m pytest -q` (run after every
  session or subagent step) and `python -m ruff check <files you changed>`.

## Architecture
Layers: routes/ → services/ → repositories/. Calls only go left to right.
- routes/api.py: HTTP only. Read the request, call one service function, return `jsonify(...)`.
  No logic here, and never touch TASKS or USERS directly.
- services/: business logic and validation. Raises AppError subclasses.
- repositories/: does not exist yet. Data lives in `TASKS` (services/tasks.py) and
  `USERS` (services/users.py). Do not create repositories/ unless asked.
- Canonical example: `get_user` in services/users.py + `get_user_route` in routes/api.py.
- Layer boundary: a route in routes/api.py passes the raw query value or the whole
  `request.get_json(silent=True)` body to exactly one services/ function and never checks or
  defaults it; all type, value, and body-shape validation lives in services/, following the
  `get_user` pattern in services/users.py.
- Errors: a service raises e.g. `NotFoundError("Task")` → `handle_app_error` in
  routes/api.py turns it into `{"error": message}` with the right status code.
- app.py registers the `api` blueprint with `url_prefix="/api"`.

## Conventions
- services/users.py is the pattern to follow for every service function.
- Type hints on every parameter and return value, e.g. `def get_task(task_id: int) -> dict:`
- Google-style docstrings with `Args:`, `Returns:`, `Raises:` sections, like `get_user`.
- Use AppError subclasses from utils/errors.py. Never raise a plain Exception and
  never let a raw KeyError escape.
  - Missing ID → `NotFoundError("Task")` (404)
  - Bad input → `ValidationError("title", "cannot be empty")` (422)
- Check before you look up: `if task_id not in TASKS: raise NotFoundError("Task")`
- New error type needed? Ask first, then subclass AppError in utils/errors.py.
- Every new service function gets a test in tests/test_tasks.py.

## Do not touch
- Do not change the signatures of `process_order`, `get_task`, or `create_task` in
  services/tasks.py. routes/api.py and tests/test_tasks.py call them.
- Do not edit, delete, or weaken existing tests in tests/test_tasks.py to make them
  pass. Fix the code, or add a new test.
- Do not change `AppError.__init__` or its `message` / `status_code` attributes in
  utils/errors.py. `handle_app_error` in routes/api.py depends on them.
- Do not change URLs in routes/api.py or the `/api` prefix in app.py.
- Do not add packages to requirements.txt without asking (Flask + pytest only).
- Do not parse, default, or validate request bodies in new routes in routes/api.py
  (no `get_json(...) or {}`, no `data.get("field")`). Pass the whole body to the services/
  function, like `update_task_route` does.
- Do not reformat, reorder, or remove existing import lines in routes/api.py, services/*.py,
  or tests/*.py. Only add the one new name you need to an existing import.
- Do not rewrite routes/api.py or services/users.py as a whole file, and do not write to them
  with shell commands (`cat >>`, Python scripts). Use targeted edits so existing routes and
  functions stay unchanged.
- If a task seems to need any of the above, stop and explain why instead of editing.