"""PreToolUse hook for task-manager.

Claude Code sends the pending tool call as JSON on stdin. Exiting with code 2
blocks the call, and whatever we print to stderr is shown to Claude as the reason.
Exit 0 lets the call go through.
"""
import json
import re
import sys

# Files Claude may never write to with Write/Edit/MultiEdit.
# Week 7 note: these same paths should also be blocked for MCP tool calls
# (mcp__<server>__<tool>) that write files, e.g. a filesystem server's write_file.
BLOCKED_PATHS = [
    "utils/errors.py",   # AppError contract that handle_app_error depends on
    "requirements.txt",  # no new packages without asking
]

# Files Claude can write, but only if the new content has no hardcoded DB URL.
CONTENT_GUARDED = ["services/tasks.py"]
DB_URL = re.compile(r"\b(postgresql|sqlite)://")

# Dangerous shell commands, matched on word boundaries rather than substrings.
BLOCKED_COMMANDS = [
    (re.compile(r"\b(DROP|TRUNCATE)\s+TABLE\b", re.IGNORECASE),
     "destructive SQL (DROP/TRUNCATE TABLE)"),
    (re.compile(r"\brm\s+-[a-zA-Z]*(r[a-zA-Z]*f|f[a-zA-Z]*r)"),
     "recursive force delete (rm -rf)"),
    (re.compile(r"\bgit\s+push\b.*(--force\b|--force-with-lease\b|\s-f\b)"),
     "git force-push"),
]

# Vector 2 fix: shell commands that write to a file (redirects, tee, sed -i, cp/mv/rm,
# PowerShell cmdlets, Python open()) are checked against BLOCKED_PATHS too.
WRITE_OPS = re.compile(
    r">|\btee\b|\bsed\s+-i\b|\b(cp|mv|rm|truncate|dd)\b|"
    r"Set-Content|Add-Content|Out-File|Remove-Item|Move-Item|Copy-Item|open\(|write_text",
    re.IGNORECASE,
)

def block(reason: str) -> None:
    print(f"BLOCKED by guard_writes.py: {reason}", file=sys.stderr)
    sys.exit(2)


def new_content(tool_name: str, tool_input: dict) -> str:
    """Return the text this Write/Edit/MultiEdit call would put into the file."""
    if tool_name == "Write":
        return tool_input.get("content", "")
    if tool_name == "Edit":
        return tool_input.get("new_string", "")
    if tool_name == "MultiEdit":
        return "\n".join(e.get("new_string", "") for e in tool_input.get("edits", []))
    return ""


def check_file_write(tool_name: str, tool_input: dict) -> None:
        # Windows paths are case-insensitive, so compare in lowercase (Vector 1 fix)
    path = tool_input.get("file_path", "").replace("\\", "/").lower()

    for blocked in BLOCKED_PATHS:
        if path.endswith(blocked):
            block(f"{blocked} is a protected file. Ask the user before changing it.")

    for guarded in CONTENT_GUARDED:
        if path.endswith(guarded) and DB_URL.search(new_content(tool_name, tool_input)):
            block(f"hardcoded database connection string in {guarded}. "
                  "Connection strings must come from environment variables "
                  "(e.g. os.environ['DATABASE_URL']), never from source code.")


def check_bash(tool_input: dict) -> None:
    command = tool_input.get("command", "")
    for pattern, label in BLOCKED_COMMANDS:
        if pattern.search(command):
            block(f"{label} is not allowed in this project.")

    normalized = command.replace("\\", "/").lower()
    for blocked in BLOCKED_PATHS:
        if blocked in normalized and WRITE_OPS.search(command):
            block(f"this shell command writes to {blocked}, which is a protected file. "
                  "Ask the user before changing it.")


def main() -> None:
    event = json.load(sys.stdin)
    tool_name = event.get("tool_name", "")
    tool_input = event.get("tool_input", {})

    if tool_name in ("Write", "Edit", "MultiEdit"):
        check_file_write(tool_name, tool_input)
    elif tool_name == "Bash":
        check_bash(tool_input)

    sys.exit(0)


if __name__ == "__main__":
    main()