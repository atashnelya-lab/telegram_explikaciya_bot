
import json, re, asyncio, os
from aiogram import Bot, Dispatcher
from aiogram.types import Message
from aiogram.filters import Command

TOKEN = os.getenv("BOT_TOKEN")  # <- set on the hosting platform (ENV VAR)
if not TOKEN:
    raise RuntimeError("Please set BOT_TOKEN environment variable")

DATA_FILE = "explikaciya_mapping.json"

with open(DATA_FILE, "r", encoding="utf-8") as f:
    data = json.load(f)

CODE2NAME: dict[str, str] = data["code_to_name"]
NAME2CODES: dict[str, list[str]] = data["name_to_codes"]

def norm(s: str) -> str:
    import re
    return re.sub(r"\s+", " ", s).strip().lower()

def find_by_code(user_code: str) -> str:
    code = user_code.strip().upper()
    if code in CODE2NAME:
        return f"Код: {code}\nНаименование: {CODE2NAME[code]}"
    like = [c for c in CODE2NAME if code in c]
    if like:
        head = "\n".join(f"• {c} — {CODE2NAME[c]}" for c in sorted(like)[:50])
        tail = "" if len(like) <= 50 else "\n… (показаны первые 50)"
        return f"Нашёл похожие коды ({len(like)}):\n{head}{tail}"
    return "Ничего не найдено по этому коду."

def find_by_name(user_name: str) -> str:
    q = norm(user_name)
    if q in NAME2CODES:
        codes = ", ".join(sorted(set(NAME2CODES[q])))
        return f"Наименование: {user_name.strip()}\nКоды: {codes}"
    hits = [(n, NAME2CODES[n]) for n in NAME2CODES if q in n]
    if hits:
        lines = []
        for n, cs in sorted(hits, key=lambda x: len(x[0]))[:30]:
            codes = ", ".join(sorted(set(cs)))
            lines.append(f"• {n}\n  Коды: {codes}")
        more = "" if len(hits) <= 30 else "\n… (показаны первые 30)"
        return f"Нашёл похожие наименования ({len(hits)}):\n" + "\n".join(lines) + more
    words = [w for w in q.split() if w]
    hits = [(n, NAME2CODES[n]) for n in NAME2CODES if all(w in n for w in words)]
    if hits:
        lines = []
        for n, cs in sorted(hits, key=lambda x: len(x[0]))[:30]:
            codes = ", ".join(sorted(set(cs)))
            lines.append(f"• {n}\n  Коды: {codes}")
        more = "" if len(hits) <= 30 else "\n… (показаны первые 30)"
        return f"Нашёл по совпадению слов ({len(hits)}):\n" + "\n".join(lines) + more
    return "Ничего не найдено по этому наименованию."

dp = Dispatcher()

@dp.message(Command("start"))
async def start(m: Message):
    await m.answer(
        "Экспликация. Команды:\n"
        "/bycode <КОД> — наименование по коду\n"
        "/byname <НАИМЕНОВАНИЕ> — коды по наименованию\n\n"
        "Примеры:\n/bycode A0UJA\n/byname Реакторное здание"
    )

@dp.message(Command("bycode"))
async def bycode(m: Message):
    parts = m.text.split(maxsplit=1)
    if len(parts) < 2:
        await m.answer("Укажите код: /bycode A0UJA")
        return
    await m.answer(find_by_code(parts[1]))

@dp.message(Command("byname"))
async def byname(m: Message):
    parts = m.text.split(maxsplit=1)
    if len(parts) < 2:
        await m.answer("Укажите наименование: /byname Реакторное здание")
        return
    await m.answer(find_by_name(parts[1]))

async def main():
    bot = Bot(TOKEN, parse_mode=None)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
