
import os
import json
import csv
from aiogram import Bot, Dispatcher, Router, F
from aiogram.types import Message
from aiogram.filters import Command
import asyncio
from typing import Dict, List, Tuple

TOKEN = os.getenv("BOT_TOKEN")
if not TOKEN:
    raise RuntimeError("Please set BOT_TOKEN environment variable")

DATA_JSON = "explikaciya_mapping.json"
DATA_CSV  = "explikaciya_codes_names.csv"

# In-memory indexes
CODE2NAME: Dict[str, str] = {}
NAME2CODES: Dict[str, List[str]] = {}

def _norm_code(s: str) -> str:
    return (s or "").strip().upper().replace(" ", "")

def _norm_name(s: str) -> str:
    return " ".join((s or "").strip().lower().split())

def load_mapping() -> Tuple[int, int]:
    global CODE2NAME, NAME2CODES
    CODE2NAME, NAME2CODES = {}, {}

    def add_pair(code: str, name: str):
        c = _norm_code(code)
        if not c or not name:
            return
        CODE2NAME[c] = name.strip()
        nn = _norm_name(name)
        NAME2CODES.setdefault(nn, [])
        if c not in NAME2CODES[nn]:
            NAME2CODES[nn].append(c)

    # Prefer JSON if present and not empty
    if os.path.exists(DATA_JSON) and os.path.getsize(DATA_JSON) > 2:
        with open(DATA_JSON, "r", encoding="utf-8") as f:
            data = json.load(f)
        # Support two popular layouts:
        if isinstance(data, dict) and "code_to_name" in data and "name_to_codes" in data:
            for c, n in data["code_to_name"].items():
                add_pair(c, n)
        elif isinstance(data, dict):
            # assume {code: name}
            for c, n in data.items():
                add_pair(c, n)
    # Fallback to CSV
    elif os.path.exists(DATA_CSV) and os.path.getsize(DATA_CSV) > 2:
        with open(DATA_CSV, "r", encoding="utf-8", newline="") as f:
            reader = csv.DictReader(f)
            for row in reader:
                add_pair(row.get("code") or row.get("CODE") or row.get("Code"),
                         row.get("name") or row.get("NAME") or row.get("Name"))
    return (len(CODE2NAME), len(NAME2CODES))

load_mapping()

router = Router()
dp = Dispatcher()
dp.include_router(router)

# Per-user pending action: "code" or "name"
PENDING: Dict[int, str] = {}

HELP = (
    "Экспликация. Команды:\n"
    "/bycode <КОД> — наименование по коду\n"
    "/byname <НАИМЕНОВАНИЕ> — коды по наименованию\n\n"
    "Можно вводить без аргумента: бот спросит, что ввести.\n"
    "/reload — перечитать список без перезапуска."
)

@router.message(Command("start"))
async def cmd_start(msg: Message):
    await msg.answer(HELP)

@router.message(Command("reload"))
async def cmd_reload(msg: Message):
    c, n = load_mapping()
    await msg.answer(f"✅ Список обновлён. {c} кодов, {n} наименований.")

async def handle_bycode_query(msg: Message, code_text: str):
    code = _norm_code(code_text)
    if not code:
        await msg.answer("Введите код, например: A0UJA")
        return
    name = CODE2NAME.get(code)
    if name:
        await msg.answer(f"Код: {code}\nНаименование: {name}")
    else:
        await msg.answer("Ничего не найдено по этому коду.")

async def handle_byname_query(msg: Message, name_text: str):
    nn = _norm_name(name_text)
    if not nn:
        await msg.answer("Введите наименование, например: Реакторное здание")
        return
    codes = NAME2CODES.get(nn, [])
    if codes:
        codes_str = ", ".join(sorted(codes))
        original = CODE2NAME.get(codes[0], name_text)
        await msg.answer(f"Наименование: {original}\nКоды: {codes_str}")
    else:
        # попытка мягкого поиска по подстроке
        nn_parts = nn.split()
        found = []
        for k, v in CODE2NAME.items():
            vv = _norm_name(v)
            if all(p in vv for p in nn_parts):
                found.append((k, v))
        if found:
            # покажем максимум 20
            lines = [f"{c} — {n}" for c, n in found[:20]]
            more = "" if len(found) <= 20 else f"\n…и ещё {len(found)-20}"
            await msg.answer("Найдено по подстроке:\n" + "\n".join(lines) + more)
        else:
            await msg.answer("Ничего не найдено по этому наименованию.")

@router.message(Command("bycode"))
async def cmd_bycode(msg: Message):
    parts = (msg.text or "").split(maxsplit=1)
    if len(parts) == 2:
        await handle_bycode_query(msg, parts[1])
    else:
        PENDING[msg.from_user.id] = "code"
        await msg.answer("Введите код (например, A0UJA):")

@router.message(Command("byname"))
async def cmd_byname(msg: Message):
    parts = (msg.text or "").split(maxsplit=1)
    if len(parts) == 2:
        await handle_byname_query(msg, parts[1])
    else:
        PENDING[msg.from_user.id] = "name"
        await msg.answer("Введите наименование (например, Реакторное здание):")

@router.message(F.text)
async def any_text(msg: Message):
    # обработка ожиданий
    pending = PENDING.pop(msg.from_user.id, None)
    if pending == "code":
        await handle_bycode_query(msg, msg.text or "")
    elif pending == "name":
        await handle_byname_query(msg, msg.text or "")
    else:
        # подсказка
        if msg.text and msg.text.strip().startswith("/"):
            return
        await msg.answer("Используйте /bycode или /byname. Для справки — /start.")

async def main():
    bot = Bot(token=TOKEN, parse_mode="HTML")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
