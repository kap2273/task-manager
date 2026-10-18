# Use this after adding or changing a service function to cover its happy path and every error it raises; don't use it to fix failing tests or to change existing ones.

Write missing tests for $ARGUMENTS (format: `<service file> <function name>`, for example
`services/tasks.py process_order`).

## Goal
The function named in $ARGUMENTS has one happy-path test plus one test for each error listed
in its docstring's Raises: section, and they all pass.

## Context
- Tests for services/tasks.py go at the end of tests/test_tasks.py; tests for
  services/users.py go at the end of tests/test_users.py. Any other service file gets
  tests/test_<resource>.py.
- Follow the style of the existing tests in that file (naming, fixtures, how they reset data).
- Expected errors come from utils/errors.py: check them with
  `pytest.raises(NotFoundError)` or `pytest.raises(ValidationError)`.

## Constraints
- Only add new test functions. Do not edit, rename, delete, or weaken any existing test.
- Do not change the function under test or any other file in services/. If a test fails
  because the code is wrong, stop and report it instead of fixing the code.
- Skip any case that an existing test already covers, and say which test covers it.
- One assertion focus per test, named `test_<function>_<case>`.

## Verification
1. Run `python -m pytest -q` and confirm the new tests pass and the old count did not drop.
2. Run `python -m ruff check` on the test file you changed. Your new tests must be clean. If ruff flags errors in old tests you didn't write, list them separately and don't count them as a failure.
3. Print a list of the cases you added and the cases you skipped (with the existing test name).
