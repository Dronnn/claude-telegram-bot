# bot.py
import asyncio
import logging
import os
from collections.abc import Awaitable, Callable
from typing import Any, Optional

from aiogram import BaseMiddleware, Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.filters import Command
from aiogram.types import BotCommand, Message, TelegramObject
from dotenv import load_dotenv

from claude_cli import ClaudeCLI, Mode, MODE_LABELS
from message_utils import split_message

load_dotenv()

BOT_TOKEN = os.environ["BOT_TOKEN"]
ALLOWED_USER_ID = int(os.environ["ALLOWED_USER_ID"])
WORK_DIR = os.environ["WORK_DIR"]

if not os.path.isdir(WORK_DIR):
    os.makedirs(WORK_DIR, exist_ok=True)

cli = ClaudeCLI(work_dir=WORK_DIR)
dp = Dispatcher()

# State
current_mode = Mode.SAFE
current_session: Optional[str] = None
usage_stats = {
    "total_cost_usd": 0.0,
    "total_turns": 0,
    "total_duration_ms": 0,
    "request_count": 0,
}


class AuthMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        if isinstance(event, Message) and (
            event.from_user is None or event.from_user.id != ALLOWED_USER_ID
        ):
            return  # Silently ignore
        return await handler(event, data)


dp.message.middleware(AuthMiddleware())


@dp.message(Command("start"))
async def cmd_start(message: Message) -> None:
    await message.answer(
        "CLI Bridge\n\n"
        "Отправьте текст — он будет передан в CLI.\n\n"
        "Команды:\n"
        "/new — новая сессия\n"
        "/safe — режим только чтение\n"
        "/write — режим запись (Write + Edit)\n"
        "/full — полный доступ\n"
        "/status — текущий статус\n"
        "/usage — статистика использования"
    )


@dp.message(Command("new"))
async def cmd_new(message: Message) -> None:
    global current_session
    current_session = None
    await message.answer("Новая сессия начата.")


@dp.message(Command("safe"))
async def cmd_safe(message: Message) -> None:
    global current_mode
    current_mode = Mode.SAFE
    await message.answer("Режим: только чтение")


@dp.message(Command("write"))
async def cmd_write(message: Message) -> None:
    global current_mode
    current_mode = Mode.WRITE
    await message.answer("Режим: запись (Write + Edit в рабочей папке)")


@dp.message(Command("full"))
async def cmd_full(message: Message) -> None:
    global current_mode
    current_mode = Mode.FULL
    await message.answer(
        "Режим: ПОЛНЫЙ ДОСТУП\n"
        "CLI может выполнять любые команды на всём компьютере.\n"
        "Используйте /safe или /write чтобы вернуться."
    )


@dp.message(Command("usage"))
async def cmd_usage(message: Message) -> None:
    cost = usage_stats["total_cost_usd"]
    turns = usage_stats["total_turns"]
    duration = usage_stats["total_duration_ms"]
    requests = usage_stats["request_count"]
    duration_min = duration / 60000
    await message.answer(
        f"Использование (с момента запуска бота):\n\n"
        f"Запросов: {requests}\n"
        f"Стоимость: ${cost:.4f}\n"
        f"Ходов CLI: {turns}\n"
        f"Время CLI: {duration_min:.1f} мин"
    )


@dp.message(Command("status"))
async def cmd_status(message: Message) -> None:
    session_display = current_session[:12] + "..." if current_session else "нет"
    await message.answer(
        f"Режим: {MODE_LABELS[current_mode]}\n"
        f"Сессия: {session_display}\n"
        f"Рабочая папка: {WORK_DIR}"
    )


@dp.message()
async def handle_message(message: Message) -> None:
    if not message.text:
        return

    global current_session
    waiting = await message.answer("...")
    try:
        text, session_id, stats = await cli.run(message.text, current_mode, current_session)
        if session_id:
            current_session = session_id
        if stats:
            usage_stats["total_cost_usd"] += stats.get("cost_usd", 0)
            usage_stats["total_turns"] += stats.get("num_turns", 0)
            usage_stats["total_duration_ms"] += stats.get("duration_ms", 0)
            usage_stats["request_count"] += 1
        await waiting.delete()
        if not text.strip():
            text = "(empty response)"
        for part in split_message(text):
            await message.answer(part)
    except asyncio.TimeoutError:
        await waiting.edit_text("Timeout: CLI did not respond within 5 minutes.")
    except Exception as e:
        logging.exception("CLI error")
        await waiting.edit_text(f"Error: {e}")


async def main() -> None:
    bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=None))
    await bot.set_my_commands([
        BotCommand(command="new", description="Новая сессия"),
        BotCommand(command="safe", description="Режим: только чтение"),
        BotCommand(command="write", description="Режим: запись (Write + Edit)"),
        BotCommand(command="full", description="Режим: полный доступ"),
        BotCommand(command="status", description="Текущий статус"),
        BotCommand(command="usage", description="Статистика использования"),
    ])
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
