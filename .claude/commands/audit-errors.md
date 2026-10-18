Audit error handling in $ARGUMENTS and fix any function that does not use the AppError pattern.

## Goal
Every public function in $ARGUMENTS raises an AppError subclass from utils/errors.py for
missing records and bad input. No function lets a raw KeyError, ValueError, or plain
Exception escape.

## Context
- Error classes live in utils/errors.py: `NotFoundError("Task")` gives a 404 and
  `ValidationError("title", "cannot be empty")` gives a 422.
- Canonical pattern: `get_user` in services/users.py. It checks before it looks up:
  `if user_id not in USERS: raise NotFoundError("User")`.
- routes/api.py has `handle_app_error`, which turns any AppError into
  `{"error": message}` with the right status code. Routes never need their own try/except.
- Example of a function that needs fixing: `process_order` in services/tasks.py does
  `TASKS[task_id]` with no check, so a bad ID raises a raw KeyError (500).

## Constraints
- Idempotency: if a function already checks its inputs and raises the right AppError
  subclass, skip it. Do not rewrite, reformat, or "improve" it. Report it as "already OK".
- Only edit $ARGUMENTS. Do not touch utils/errors.py, routes/api.py, or anything in tests/.
- Do not change any function signature (name, parameters, defaults, return type).
- Do not add new AppError subclasses. If a case does not fit NotFoundError or
  ValidationError, stop and ask.
- Fix one function at a time with a targeted edit. Never rewrite the whole file.
- If a fixed function has no Raises: section in its docstring, add one.
- If a fix would change the status code an existing input gets (for example 404 to 422), list each change and ask before editing.

## Verification
After every function you change (not when done):
1. Run `python -m pytest -q` and confirm nothing that passed before now fails.
2. Run `python -m ruff check $ARGUMENTS`.
If either fails, fix that function before moving to the next one.

At the end, print a table with one row per function: name, status
(already OK / fixed), and the error class it now raises.
