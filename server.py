# server.py
import asyncio
from fastapi import FastAPI

# Импортируем функцию main() из твоего bot.py
from bot import main as run_bot

app = FastAPI()

@app.get("/")
def root():
    return {"status": "ok", "service": "telegram_explikaciya_bot"}

@app.on_event("startup")
async def on_startup():
    # Запускаем Telegram-бота в фоне,
    # а uvicorn будет держать порт для Render
    asyncio.create_task(run_bot())
