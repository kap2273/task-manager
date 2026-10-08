# Week 4 Drill 1 — CLAUDE.md Audit and Repair

## Goal
Diagnose a weak CLAUDE.md through real Claude Code sessions,
then repair it based on what you observe going wrong.

## Setup
    pip install flask pytest
    pytest -v   # you should see 2 pass, 2 fail before starting

Reset services/tasks.py between runs:
    git checkout services/tasks.py
(or manually restore the original file from the original zip)

---

## Phase 1 — Expose the flaws (20 min)

Run these three prompts against the project AS-IS with the current
weak CLAUDE.md. After each prompt, record your observations below.

### Prompt 1
```
Goal: Add a new endpoint to create a product.
Constraints: Do not change any existing endpoints.
Verification: Run pytest -v when done.
```

Observations after Prompt 1:
- Did Claude ask a clarifying question it shouldn't have needed to?
- Did Claude introduce a style inconsistent with the codebase?
- Did Claude touch a file it shouldn't have?
- Did Claude use the wrong error handling pattern?

---

### Prompt 2
```
Goal: Fix the failing tests in tests/test_tasks.py.
Constraints: Do not modify the test file itself.
Verification: Run pytest tests/test_tasks.py -v when done.
```

Observations after Prompt 2:
- Did Claude fix the tests the right way (using AppError subclasses)?
- Did Claude add type hints and docstrings?
- Did Claude follow the pattern in services/users.py?

---

### Prompt 3
```
Goal: Refactor the get_task function in services/tasks.py
      to be more consistent with the rest of the codebase.
Constraints: Do not change the function signature.
Verification: Run pytest -v when done.
```

Observations after Prompt 3:
- Did Claude match the style of services/users.py?
- Did Claude use the correct error class from utils/errors.py?
- Did Claude need to be corrected or given follow-up prompts?

---

## Phase 2 — Repair CLAUDE.md (20 min)

For each flaw you observed in Phase 1, add a targeted fix to CLAUDE.md.
For every line you add, write one sentence justifying it:
"I'm adding this because Claude did X in Prompt Y."

Open CLAUDE.md and rewrite it now. Aim for the four-part structure:

```markdown
# Task Manager

[brief project description]

## Commands
[what Claude needs to run, test, lint]

## Architecture
[patterns Claude must follow — repository, error handling, etc.]

## Conventions
[style rules — type hints, docstrings, naming]

## Do not touch
[hard off-limits rules]
```

---

## Phase 3 — Verify the repair (10 min)

Re-run the same three prompts with your repaired CLAUDE.md.
Count how many follow-up corrections were needed this time vs Phase 1.

---

## Debrief questions
1. Which flaw in the original CLAUDE.md caused the most damage
   across all three prompts?
2. What is the difference between "Use good variable names" and
   "Follow the pattern in services/users.py"? Why does one work
   and the other doesn't?
3. What would you add to CLAUDE.md if you ran a fourth prompt
   and Claude got something wrong again?

---

## Reference: what a repaired CLAUDE.md might look like

(Do not read until after you have written your own version)

```markdown
# Task Manager

Python 3.12 REST API using Flask.
Manages tasks and users.

## Commands
- Install: pip install -r requirements.txt
- Run tests: pytest -v
- Lint: ruff check .

## Architecture
- Custom errors only: use AppError subclasses from utils/errors.py
  — never raise raw KeyError, ValueError, or plain Exception
- See services/users.py for the canonical service pattern

## Conventions
- All functions require type hints and Google-style docstrings
- New endpoints need a corresponding test in tests/
- Follow the error handling and docstring style in services/users.py

## Do not touch
- Do not modify tests/ files directly
- Do not add new dependencies without updating requirements.txt
```
