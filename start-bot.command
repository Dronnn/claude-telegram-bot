#!/bin/bash
cd "$(dirname "$0")"
source .venv/bin/activate
echo "Bot is starting... Press Ctrl+C to stop."
echo "---"
python bot.py
