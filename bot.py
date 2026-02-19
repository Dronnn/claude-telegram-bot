# bot.py
import asyncio
import logging
import os
from collections.abc import Awaitable, Callable
from typing import Any, Optional

from aiogram import BaseMiddleware, Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.filters import Command
from aiogram.types import Message, TelegramObject
from dotenv import load_dotenv

from claude_cli import ClaudeCLI, Mode, MODE_LABELS
from message_utils import split_message

load_dotenv()

BOT_TOKEN = os.environ["BOT_TOKEN"]
ALLOWED_USER_ID = int(os.environ["ALLOWED_USER_ID"])
WORK_DIR = os.environ["WORK_DIR"]

cli = ClaudeCLI(work_dir=WORK_DIR)
dp = Dispatcher()

# State
current_mode = Mode.SAFE
current_session: Optional[str] = None


class AuthMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        if isinstance(event, Message) and event.from_user.id != ALLOWED_USER_ID:
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
        "/status — текущий статус"
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

    text, session_id = await cli.run(message.text, current_mode, current_session)

    if session_id:
        current_session = session_id

    await waiting.delete()

    for part in split_message(text):
        await message.answer(part)


async def main() -> None:
    bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=None))
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
