# Claude Code Telegram Bridge

Control [Claude Code](https://docs.anthropic.com/en/docs/claude-code) from your phone via Telegram. Send messages to your bot — it runs Claude Code CLI on your Mac and sends the response back.

```
You (phone) --> Telegram Bot --> Claude Code CLI (Mac) --> Telegram Bot --> You (phone)
```

## Why?

Claude Code runs in your terminal. You step away from your desk. Now you can't use it. This bot fixes that — open Telegram on your phone, type a message, get a response from Claude Code running on your Mac. Your subscription, your machine, no API costs.

## Features

- **Three permission modes** — switch on the fly:
  - `/safe` — read-only (default). Claude can read files and answer questions.
  - `/write` — Claude can create and edit files in the working directory.
  - `/full` — full access (use with caution).
- **Session continuity** — conversation context is preserved across messages.
- **Single-user auth** — only your Telegram account can use the bot.
- **Long response splitting** — automatically splits responses that exceed Telegram's 4096 character limit.
- **Timeout protection** — 5-minute timeout prevents the bot from hanging on slow requests.
- **One-click launch** — double-click `start-bot.command` in Finder to start.

## Requirements

- macOS with [Claude Code](https://docs.anthropic.com/en/docs/claude-code) installed and authenticated
- Python 3.9+
- A Telegram bot token (from [@BotFather](https://t.me/BotFather))

## Setup

**1. Clone and create virtual environment:**

```bash
git clone <your-repo-url>
cd claude-telegram-bot
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

**2. Create a Telegram bot:**

- Message [@BotFather](https://t.me/BotFather) on Telegram
- Send `/newbot` and follow the prompts
- Copy the bot token

**3. Get your Telegram user ID:**

- Message [@userinfobot](https://t.me/userinfobot) on Telegram
- It will reply with your numeric ID

**4. Configure:**

```bash
cp .env.example .env
```

Edit `.env`:

```
BOT_TOKEN=123456789:ABCdefGHIjklMNOpqrsTUVwxyz
ALLOWED_USER_ID=987654321
WORK_DIR=/path/to/your/working/directory
```

`WORK_DIR` is the directory where Claude Code will operate — it can read, create, and edit files there (in `/write` mode).

**5. Run:**

```bash
source .venv/bin/activate
python bot.py
```

Or double-click `start-bot.command` in Finder.

**6. Stop:** `Ctrl+C` in the terminal, or close the terminal window.

## Bot Commands

| Command | Description |
|---------|-------------|
| `/start` | Show help |
| `/new` | Start a new session (clear conversation context) |
| `/safe` | Switch to read-only mode (default) |
| `/write` | Switch to write mode (can create/edit files in WORK_DIR) |
| `/full` | Switch to full access mode |
| `/status` | Show current mode, session, and working directory |

## Permission Modes

| Mode | What Claude can do | CLI flags |
|------|-------------------|-----------|
| Safe | Read files, answer questions | `claude -p` |
| Write | + Create and edit files in WORK_DIR | `claude -p --allowedTools Write Edit` |
| Full | Everything, anywhere on the machine | `claude -p --dangerously-skip-permissions` |

The bot starts in **safe** mode. Switch modes anytime with `/safe`, `/write`, or `/full`.

## Architecture

```
bot.py              — Telegram bot (aiogram 3.x, long-polling)
claude_cli.py       — Claude Code CLI wrapper (async subprocess)
message_utils.py    — Message splitting for Telegram's 4096 char limit
```

The bot passes your messages to `claude -p` (non-interactive print mode) via stdin and parses the JSON response. Sessions are maintained using `--resume` with session IDs from the CLI output.

## Security

- **Single-user only** — messages from any Telegram account other than `ALLOWED_USER_ID` are silently ignored.
- **No API keys** — uses your existing Claude Code subscription via the CLI.
- **Tokens stay local** — `.env` is gitignored, never committed.
- **Safe by default** — starts in read-only mode. Write/full modes require explicit opt-in.

## License

MIT
