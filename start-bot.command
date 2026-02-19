#!/bin/bash
cd "$(dirname "$0")"
if [ ! -d .venv ]; then
    echo "Error: .venv not found. Run 'python3 -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt' first."
    exit 1
fi
source .venv/bin/activate
echo "Bot is starting... Press Ctrl+C to stop."
echo "---"
python bot.py
