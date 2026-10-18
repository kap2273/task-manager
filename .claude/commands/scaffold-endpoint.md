Scaffold a new API endpoint. $ARGUMENTS contains two words: the first is the resource name
(for example `tags`) and the second is the HTTP method (GET, POST, PATCH, or DELETE).

## Goal
Add a working endpoint for the resource and method given in $ARGUMENTS. These files must be
created or updated:
- Route file: routes/api.py (add one new route function)
- Service file: services/<resource>.py (create it if it doesn't exist, add one service function)
- Schema file: schemas/<resource>.py (create it if it doesn't exist; holds the resource's
  REQUIRED_FIELDS and ALLOWED_FIELDS tuples, plain Python, no new libraries)
- Test file: tests/test_<resource>.py (new file, one happy-path test)

## Context
- The canonical route pattern is routes/tasks.py. In this repo the task routes live in
  routes/api.py, so follow `get_task_route` (GET) and `update_task_route` (body-taking
  methods) there.
- Service pattern: `get_user` in services/users.py. Type hints, Google-style docstring with
  Args/Returns/Raises, and AppError subclasses from utils/errors.py.
- Data is stored in an in-memory dict in the service file, like `TASKS` in services/tasks.py.
- `handle_app_error` in routes/api.py already turns AppErrors into JSON responses.

## Constraints
- No business logic in the route handler. The route reads the URL param or
  `request.get_json(silent=True)`, passes it to exactly one service function, and returns
  `jsonify(...)`. No if-statements, no `.get()` defaults, no validation in the route.
- All validation goes in the service function, using the fields from schemas/<resource>.py.
- Do not change any existing route, URL, or import line in routes/api.py. Only add the new
  import name and the new route.
- Do not edit utils/errors.py or any existing file in tests/.
- Do not add packages to requirements.txt.
- If the fields for the resource are not obvious from $ARGUMENTS, ask which fields it needs before writing schemas/<resource>.py.

## Verification
1. Run `python -m pytest -q`. Every test must pass, old and new.
2. The new test in tests/test_<resource>.py uses Flask's test client to call the new
   endpoint on a happy path and asserts the status code: 201 for POST, 200 for GET and
   PATCH, 204 for DELETE.
3. Run `python -m ruff check` on every file you created or changed.
