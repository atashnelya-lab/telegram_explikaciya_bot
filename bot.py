# bot.py
import os, json, csv, re, asyncio
from aiogram import Bot, Dispatcher
from aiogram.types import Message
from aiogram.filters import Command

# ====== TOKEN ======
TOKEN = os.getenv("BOT_TOKEN") or "8022401482:AAFsdK8f1TF6AkZlX7MLtCvel3RtjpMtIv8"
if not TOKEN:
    raise RuntimeError("Please set BOT_TOKEN environment variable")

# ====== LOAD DATA (CSV first, then JSON fallback) ======
CSV_PATH = "data/explikaciya.csv"
JSON_PATH = "explikaciya_mapping.json"

def load_mapping():
    code2name = {}
    name2codes = {}
    if os.path.exists(CSV_PATH):
        with open(CSV_PATH, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                code = (row.get("code") or "").strip().upper()
                name = (row.get("name") or "").strip()
                if not code or not name:
                    continue
                code2name[code] = name
                key = norm(name)
                name2codes.setdefault(key, []).append(code)
        return code2name, name2codes

    # Fallback на старый JSON
    with open(JSON_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    code2name = data["code_to_name"]
    name2codes = data["name_to_codes"]
    return code2name, name2codes

def norm(s: str) -> str:
    return re.sub(r"\s+", " ", (s or "").strip().lower())

CODE2NAME, NAME2CODES = load_mapping()

# ====== SIMPLE STATE (по пользователям) ======
# user_state[user_id] = "bycode" | "byname" | None
user_state: dict[int, str] = {}

bot = Bot(token=TOKEN)
dp = Dispatcher()

# ====== COMMANDS ======
@dp.message(Command("start"))
async def cmd_start(m: Message):
    await m.answer(
        "Экспликация. Команды:\n"
        "/bycode — наименование по коду (после команды просто отправьте код)\n"
        "/byname — коды по наименованию (после команды отправьте название)\n"
        "/cancel — отменить ввод\n\n"
        "Примеры:\n"
        "Код: A0UJA → Реакторное здание\n"
        "Наименование: Реакторное здание → A0UJA"
    )

@dp.message(Command("cancel"))
async def cmd_cancel(m: Message):
    user_state.pop(m.from_user.id, None)
    await m.answer("Отменено. Можете ввести /bycode или /byname.")

@dp.message(Command("bycode"))
async def cmd_bycode(m: Message):
    user_state[m.from_user.id] = "bycode"
    await m.answer("Введите код (например: A0UJA):")

@dp.message(Command("byname"))
async def cmd_byname(m: Message):
    user_state[m.from_user.id] = "byname"
    await m.answer("Введите наименование (например: Реакторное здание):")

# ====== UNIVERSAL HANDLER ======
@dp.message()
async def handle_text(m: Message):
    mode = user_state.get(m.from_user.id)
    text = (m.text or "").strip()
    if not mode:
        # Если не в режиме ввода — подскажем
        if text.startswith("/"):
            return  # другие команды игнорим
        await m.answer("Введите /bycode или /byname, затем следуйте инструкции.")
        return

    if mode == "bycode":
        code = text.upper()
        name = CODE2NAME.get(code)
        if name:
            await m.answer(f"Код: {code}\nНаименование: {name}")
        else:
            await m.answer("Ничего не найдено по этому коду.")
        user_state.pop(m.from_user.id, None)
        return

    if mode == "byname":
        key = norm(text)
        codes = NAME2CODES.get(key, [])
        if codes:
            codes_str = ", ".join(sorted(codes))
            await m.answer(f"Наименование: {text}\nКоды: {codes_str}")
        else:
            await m.answer("Коды для такого наименования не найдены.")
        user_state.pop(m.from_user.id, None)
        return

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
