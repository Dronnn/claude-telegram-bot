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
- [ ] Commit with clean message
