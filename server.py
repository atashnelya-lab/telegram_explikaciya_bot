# server.py
import asyncio
import logging
from typing import Optional

from fastapi import FastAPI
from bot import main as run_bot  # импортируем единственную корутину из bot.py

# ---------- ЛОГИ ----------
logging.basicConfig(level=logging.INFO)
log = logging.getLogger("server")

app = FastAPI(title="telegram_explikaciya_bot")

# Фоновая задача с polling'ом
_bot_task: Optional[asyncio.Task] = None


@app.on_event("startup")
async def on_startup() -> None:
    """
    При старте веб-приложения запускаем бота в отдельной
    фоновой задаче. Uvicorn держит порт, поэтому Render/Railway
    видит «живое» веб-приложение, а бот крутится параллельно.
    """
    global _bot_task
    if _bot_task is None or _bot_task.done():
        log.info("Starting Telegram bot (polling) in background task…")
        _bot_task = asyncio.create_task(run_bot())
    else:
        log.info("Bot task already running.")


@app.on_event("shutdown")
async def on_shutdown() -> None:
    """
    Аккуратно останавливаем фонового бота при остановке веб-приложения.
    """
    global _bot_task
    if _bot_task and not _bot_task.done():
        log.info("Cancelling bot background task…")
        _bot_task.cancel()
        try:
            await _bot_task
        except asyncio.CancelledError:
            pass
        log.info("Bot task cancelled.")


# --- простые эндпоинты для проверки живости сервиса ---
@app.get("/")
async def root():
    return {"status": "ok", "service": "telegram_explikaciya_bot"}

@app.get("/healthz")
async def health():
    return {"ok": True}
