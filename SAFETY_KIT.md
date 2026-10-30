# Safety kit

Four layers protect the task-manager repo, from advisory to enforced:

```
CLAUDE.md Git Conventions   advisory   Claude reads it, nothing forces it
/ship command               mixed      prompt-driven checks + a permission gate on commit
.githooks/commit-msg        enforced   git rejects bad subjects on every commit
.claude/hooks/guard_git.py  enforced   Claude Code blocks unsafe git commands
```

## Test 1: /ship stops on a debug statement

I added `print("debug: checking task")` inside `process_order` in services/tasks.py and ran `/ship`.

```
The /ship check stopped at step 1 because the diff contains a debug statement.
I didn't run the tests or propose a commit.

Debug scan hits:
- services/tasks.py:31: print( call (print("debug: checking task") in process_order)
```

It also pointed out I was on master, which comes from the CLAUDE.md rule. I reverted the file with `git checkout -- services/tasks.py`.

## Test 2: /ship completes a clean commit

On branch `feat/hooks-setup-note` I added the core.hooksPath setup line to CLAUDE.md and ran `/ship`.

```
Debug scan is clean: the one added line is a doc sentence, no print/TODO/commented code.
All 76 tests passed (python -m pytest -q).

Proposed commit message:
docs(hooks): note core.hooksPath setup after cloning
File to stage: CLAUDE.md
Shall I commit it?
```

I replied "yes, commit it". Claude Code showed a permission prompt for `git commit`, I approved it, and the commit went through as `0645d73 docs(hooks): note core.hooksPath setup after cloning`.

### Why git commit is not in allowed-tools

ship.md pre-approves `git status`, `git diff`, `git add`, `pytest` and Read, and leaves out `git commit` and `git push`. The "wait for my approval" step in the prompt is only an instruction, so the model could skip it. Leaving `git commit` out means Claude Code itself stops and asks me before every commit, so the approval can't be skipped. The cost is one extra click per commit, which is worth it. This only holds in manual mode; auto mode would approve the commit without asking, so I keep auto mode off in this project.

## Test 3: commit-msg hook rejects bad subjects

```
$ git commit --allow-empty -m "fixed stuff"
commit-msg: subject must look like 'type(scope): subject' or 'type: subject'
  allowed types: feat, fix, test, refactor, docs, chore
  got: fixed stuff
```

```
$ git commit --allow-empty -m "feat(tasks): this subject line is deliberately written to be way longer than seventy two characters"
commit-msg: subject is 99 characters, max is 72
```

No commit was created in either case.

## Test 4: commit-msg hook accepts a good subject

```
$ git commit -m "fix(hooks): extend guard_writes hook to PowerShell commands"
[fix/guard-writes-powershell 1afff3c] fix(hooks): extend guard_writes hook to PowerShell commands
 2 files changed, 2 insertions(+), 2 deletions(-)
```

Claude's commit from Test 2 also passed through this hook, so it applies to Claude's commits as well as mine.

## Test 5: guard hook blocks forbidden commands

I asked Claude to run each command as a separate tool call and not refuse on its own, so the hook would be what stopped it.

| Command Claude tried | Result |
|---|---|
| `git push --force origin feat/test` | `guard_git: blocked: force-push is not allowed` |
| `git push origin master` | `guard_git: blocked: push to master is not allowed` |
| `git commit --allow-empty --no-verify -m "test: guard check"` | `guard_git: blocked: --no-verify would skip the commit-msg hook` |

## Test 6: guard hook allows normal commands

In the same session Claude ran `git status`, which went through: on master, up to date with origin/master, working tree clean.

## Problem found while testing

Claude Code on my Windows machine runs commands through a PowerShell tool, not Bash. The output showed `PostToolUse:PowerShell`, which tipped me off. My guard hook was registered with matcher `"Bash"`, so it would never have seen Claude's commands. I changed the matcher to `"Bash|PowerShell"` (commit `e0c1db5`) and applied the same fix to my Week 6 guard_writes.py (commit `1afff3c`). Test 5 was run after the fix.

## Advisory vs enforced

| Rule | Where | Type | Why |
|---|---|---|---|
| Subject format `type(scope): subject` | CLAUDE.md + commit-msg | Enforced | Git runs the hook on every commit and rejects anything that doesn't match the regex. |
| Allowed types (feat, fix, test, refactor, docs, chore) | CLAUDE.md + commit-msg | Enforced | The type list is part of the hook's regex. |
| Subject max 72 characters | CLAUDE.md + commit-msg | Enforced | The hook counts the subject length and exits 1 if it's over. |
| Scope list (tasks, api, schemas, utils, tests, hooks) | CLAUDE.md | Advisory | The hook accepts any lowercase scope, so only the model's reading of CLAUDE.md keeps scopes on the list. |
| Lowercase start, imperative mood, no trailing period | CLAUDE.md | Advisory | The hook doesn't check these; wording rules are hard to check reliably with a regex. |
| Branch naming `feat/` / `fix/` | CLAUDE.md | Advisory | Nothing checks branch names when a branch is created. |
| Never work directly on master | CLAUDE.md | Advisory | Git allows commits on master; Claude only warns about it. |
| Run `pytest -q` before committing | CLAUDE.md + /ship | Advisory | /ship tells Claude to run tests and stop on failure, but the model is the one deciding to stop. |
| Debug scan (print, breakpoint, TODO/FIXME, commented-out code) | /ship | Advisory | The scan is the model reading the diff, so it can miss things or judge them wrong. |
| Commit only after my approval | /ship + allowed-tools | Enforced | `git commit` isn't pre-approved, so Claude Code shows a permission prompt before every commit (in manual mode). |
| One logical change per commit | CLAUDE.md | Advisory | Only the model's judgment decides what counts as one change. |
| Never edit or delete a test just to make it pass | CLAUDE.md | Advisory | No hook inspects test changes; this needs human review. |
| Never push to master/main | CLAUDE.md + guard_git.py | Enforced | Claude Code runs the hook before every Bash/PowerShell call and exit 2 cancels the command. |
| Never force-push | CLAUDE.md + guard_git.py | Enforced | Same hook; it checks `--force`, `-f`, `--force-with-lease` and `+refspec`. |
| Never use `--no-verify` | CLAUDE.md + guard_git.py | Enforced | The hook blocks `--no-verify` and `git commit -n` before Claude can skip the commit-msg hook. |
| Run `git config core.hooksPath .githooks` after cloning | CLAUDE.md | Advisory | The setting lives in .git/config, which isn't committed, so each clone has to turn it on by hand. |

The enforced rules have limits too. The guard hook only sees Claude's tool calls, not commands I type myself, and I can still run `git commit --no-verify` in my own terminal. The hooks stop mistakes, not a person who means to get around them.
