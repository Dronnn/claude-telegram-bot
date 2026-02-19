# Plan: Task 3 - Claude CLI Wrapper (TDD)

## Goal
Create an async wrapper around the `claude` CLI tool with three permission modes (safe/write/full), session support, and JSON output parsing. Follow TDD: tests first, then implementation.

## Steps

- [x] Write failing tests in `tests/test_claude_cli.py`
- [x] Run tests to verify they fail (ImportError expected)
- [x] Implement `claude_cli.py` with Mode enum, ClaudeCLI class
- [x] Add pytest-asyncio config if needed, run tests to verify all pass
- [x] Commit with clean message

---

# Plan: Task 4 - Bot Core with Auth and Commands

## Goal
Create `bot.py` — the main Telegram bot file using aiogram 3.x with auth middleware, mode switching commands, and session management.

## Steps

- [x] Create `bot.py` with auth middleware, commands, and message handler
- [x] Verify imports work via `.venv/bin/python`
- [x] Commit with clean message

---

# Plan: Code Review Bug Fixes

## Goal
Fix critical and important bugs found during code review: subprocess timeout, error handling, message splitting newline consumption, auth null check, .env.example, and WORK_DIR validation.

## Steps

- [x] Fix 1: Add subprocess timeout to claude_cli.py `_execute`
- [x] Fix 2: Add error handling (try/except) in bot.py `handle_message`
- [x] Fix 3: Fix split_message newline consumption + update tests
- [x] Fix 4: AuthMiddleware null check for `event.from_user`
- [x] Fix 5: Update .env.example WORK_DIR
- [x] Fix 6: Validate WORK_DIR at startup in bot.py
- [x] Run all tests and verify they pass
- [x] Commit all fixes

---

# Plan: Fix parse_response JSON list bug

## Goal
Fix `parse_response` in `claude_cli.py` which crashes with `AttributeError: 'list' object has no attribute 'get'` because `claude -p --output-format json` returns a JSON array, not a JSON object.

## Steps

- [x] Investigate actual JSON format from `claude -p --output-format json`
- [x] Fix `parse_response` to handle the actual format
- [x] Update tests to cover the list format
- [x] Run tests and commit
