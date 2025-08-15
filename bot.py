# bot.py — aiogram v3, безопасный polling (снимаем вебхук перед стартом)

import os
import json
import logging
from pathlib import Path
from typing import Dict, List

from aiogram import Bot, Dispatcher, Router
from aiogram.types import Message
from aiogram.filters import Command

# ---------- ЛОГИ ----------
logging.basicConfig(level=logging.INFO)
log = logging.getLogger("telegram_explikaciya_bot")

# ---------- НАСТРОЙКИ ----------
TOKEN = os.getenv("BOT_TOKEN")
if not TOKEN:
    raise RuntimeError("Environment variable BOT_TOKEN is not set")

# Файл с маппингом код <-> наименование
DATA_FILE = Path(__file__).parent / "explikaciya_mapping.json"

# Данные (загружаются из JSON)
CODE2NAME: Dict[str, str] = {}
NAME2CODES: Dict[str, List[str]] = {}

# ---------- ЗАГРУЗКА ДАННЫХ ----------
def load_mapping() -> None:
    """Подгрузить словари из JSON и нормализовать ключи."""
    global CODE2NAME, NAME2CODES

    if not DATA_FILE.exists():
        log.error("Файл с данными не найден: %s", DATA_FILE)
        CODE2NAME, NAME2CODES = {}, {}
        return

    with DATA_FILE.open("r", encoding="utf-8") as f:
        data = json.load(f)

    # ожидаем {"code_to_name": {...}, "name_to_codes": {...}}
    CODE2NAME = data.get("code_to_name", {}) or {}
    NAME2CODES = data.get("name_to_codes", {}) or {}

    # нормализация
    CODE2NAME = {str(k).strip().upper(): str(v) for k, v in CODE2NAME.items()}
    NAME2CODES = {
        str(name).strip().lower(): [str(c).strip().upper() for c in codes]
        for name, codes in NAME2CODES.items()
    }

    log.info("Загружено: %d кодов, %d наименований", len(CODE2NAME), len(NAME2CODES))


# ---------- ROUTER ----------
router = Router()


@router.message(Command("start"))
async def cmd_start(message: Message) -> None:
    text = (
        "Экспликация. Команды:\n"
        "/bycode <КОД> — наименование по коду\n"
        "/byname <НАИМЕНОВАНИЕ> — коды по наименованию\n\n"
        "Примеры:\n"
        "/bycode A0UJA\n"
        "/byname Реакторное здание"
    )
    await message.answer(text)


@router.message(Command("bycode"))
async def cmd_bycode(message: Message) -> None:
    parts = (message.text or "").split(maxsplit=1)
    if len(parts) < 2:
        await message.answer("Укажи код: например, `/bycode A0UJA`", parse_mode="Markdown")
        return

    code = parts[1].strip().upper()
    name = CODE2NAME.get(code)
    if name:
        await message.answer(f"Код: **{code}**\nНаименование: {name}", parse_mode="Markdown")
    else:
        await message.answer("Ничего не найдено по этому коду.")


@router.message(Command("byname"))
async def cmd_byname(message: Message) -> None:
    parts = (message.text or "").split(maxsplit=1)
    if len(parts) < 2:
        await message.answer(
            "Укажи наименование: например, `/byname Реакторное здание`",
            parse_mode="Markdown",
        )
        return

    name_query = parts[1].strip().lower()
    codes = NAME2CODES.get(name_query, [])

    if codes:
        await message.answer(
            f"Наименование: **{parts[1].strip()}**\nКоды: {', '.join(codes)}",
            parse_mode="Markdown",
        )
    else:
        await message.answer("Коды для такого наименования не найдены.")


# ---------- ЕДИНСТВЕННАЯ КОРУТИНА ДЛЯ server.py ----------
async def main() -> None:
    """
    Эту функцию импортирует server.py:  from bot import main as run_bot
    и запускает в on_startup (фоновой задачей).
    """
    load_mapping()

    bot = Bot(TOKEN, parse_mode="HTML")

    # ВАЖНО: снимаем любой вебхук и чистим отложенные апдейты,
    # чтобы polling был единственным источником getUpdates.
    await bot.delete_webhook(drop_pending_updates=True)

    dp = Dispatcher()
    dp.include_router(router)

    log.info("Стартуем polling…")
    await dp.start_polling(bot)
