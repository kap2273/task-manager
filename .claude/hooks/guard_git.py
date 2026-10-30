"""PreToolUse hook: block dangerous git commands before Claude runs them.

Blocks pushes to main/master, force-pushes, and anything that skips
git hooks with --no-verify. Everything else exits 0 and runs normally.
"""

import json
import os
import re
import shlex
import subprocess
import sys

PROTECTED = {"main", "master"}


def block(reason):
    print(f"guard_git: blocked: {reason}", file=sys.stderr)
    sys.exit(2)


def split_commands(command):
    # "cd x && git push; ls" -> check each piece separately
    return [p.strip() for p in re.split(r"&&|\|\||;|\||\n", command) if p.strip()]


def tokenize(part):
    try:
        return shlex.split(part)
    except ValueError:
        return part.split()


def git_subcommand(tokens):
    """Return (subcommand, args) for a git command, or (None, [])."""
    if not tokens:
        return None, []
    name = os.path.basename(tokens[0]).lower().removesuffix(".exe")
    if name != "git":
        return None, []
    i = 1
    # skip global options like -C <path> or -c key=val
    while i < len(tokens) and tokens[i].startswith("-"):
        i += 2 if tokens[i] in ("-C", "-c") else 1
    if i >= len(tokens):
        return None, []
    return tokens[i], tokens[i + 1:]


def current_branch(cwd):
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            cwd=cwd or None, capture_output=True, text=True, timeout=5,
        )
        return result.stdout.strip()
    except Exception:
        return ""


def check_push(args, cwd):
    flags = [a for a in args if a.startswith("-")]
    positional = [a for a in args if not a.startswith("-")]

    # force-push: --force, -f, -uf, --force-with-lease[=...], or a +refspec
    for f in flags:
        if f == "--force" or f.startswith("--force-with-lease"):
            block("force-push is not allowed")
        if re.fullmatch(r"-[a-zA-Z]*f[a-zA-Z]*", f):
            block("force-push is not allowed")
    if any(p.startswith("+") for p in positional[1:]):
        block("force-push (+refspec) is not allowed")

    if "--all" in flags or "--mirror" in flags:
        block("pushing all branches would include master/main")

    refspecs = positional[1:]  # positional[0] is the remote
    if not refspecs:
        # plain "git push" or "git push origin" pushes the current branch
        if current_branch(cwd) in PROTECTED:
            block("push to master/main is not allowed (you are on that branch)")
        return

    for spec in refspecs:
        src, _, dst = spec.lstrip("+").partition(":")
        target = (dst or src).removeprefix("refs/heads/")
        if target == "HEAD":
            target = current_branch(cwd)
        if target in PROTECTED:
            block(f"push to {target} is not allowed")


def main():
    try:
        payload = json.loads(sys.stdin.buffer.read().decode("utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError):
        sys.exit(0)

    command = payload.get("tool_input", {}).get("command", "")
    cwd = payload.get("cwd")

    for part in split_commands(command):
        tokens = tokenize(part)
        if "--no-verify" in tokens:
            block("--no-verify would skip the commit-msg hook")

        sub, args = git_subcommand(tokens)
        # git commit -n is short for --no-verify
        if sub == "commit" and any(re.fullmatch(r"-[a-zA-Z]*n[a-zA-Z]*", a) for a in args):
            block("git commit -n is --no-verify and would skip the commit-msg hook")
        if sub == "push":
            check_push(args, cwd)

    sys.exit(0)


if __name__ == "__main__":
    main()
