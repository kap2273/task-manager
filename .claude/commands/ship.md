---
description: Review changes for debug code, run tests, then propose a conventional commit
allowed-tools: Bash(git status:*), Bash(git diff:*), Bash(git add:*), Bash(pytest:*), Read
---

## Current state

Status:
!`git status --short`

Diff against HEAD:
!`git diff HEAD`

## What to do

Follow these steps in order. Stop at the first failure.

1. **Debug scan.** Look only at lines added in the diff above (lines starting with `+`). Also read any untracked files (`??` in status) with the Read tool. Stop and report file and line number if you find any of:
   - a `print(` or `breakpoint()` call
   - a new `TODO` or `FIXME` comment
   - commented-out code (a `#` line that is clearly code, not an explanation)
   If anything is found, list every hit as `file:line: reason` and do not continue.

2. **Tests.** Run `pytest -q`. If anything fails, show the failing tests and stop.

3. **Propose a commit.** Write one commit message following the Git Conventions in CLAUDE.md: `type(scope): subject`, max 72 characters. Show it and the list of files you will stage. Then wait for my approval.

4. **Commit.** Only after I approve, run `git add` on those files and `git commit -m "<message>"`.

Never run git push. Never use --no-verify.
