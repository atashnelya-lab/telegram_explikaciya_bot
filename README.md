
# Telegram Explikaciya Bot (без локальной установки Python)

Две функции:
1) /bycode <КОД> → наименование
2) /byname <НАИМЕНОВАНИЕ> → код(ы)

## Файлы
- `bot.py` — код бота (читает токен из переменной окружения `BOT_TOKEN`)
- `explikaciya_mapping.json` — данные (коды ↔ наименования)
- `requirements.txt` — зависимости
- `render.yaml` — для Render (фоновый worker)
- `railway.json` — для Railway

---

## Вариант A: Render (рекомендую — просто и бесплатно)
1. Создайте бота у @BotFather и получите BOT_TOKEN.
2. Зайдите на https://render.com, создайте аккаунт и нажмите **New** → **Blueprint**.
3. Подключите репозиторий с этими файлами (загрузите их на GitHub в отдельный репозиторий).
   - Render увидит `render.yaml` и предложит создать **Worker**.
4. После создания сервиса откройте **Environment** → добавьте переменную:
   - Key: `BOT_TOKEN`
   - Value: токен из @BotFather
5. В **Logs** увидите, что бот запустился. Откройте в Telegram вашего бота, нажмите **Start** и проверьте команды.

### Как быстро загрузить проект на GitHub
- Создайте новый приватный репозиторий на GitHub.
- Загрузите файлы `bot.py`, `explikaciya_mapping.json`, `requirements.txt`, `render.yaml`.
- Подключите репозиторий к Render по кнопке **New → Blueprint**.

---

## Вариант B: Railway (тоже просто)
1. Аккаунт на https://railway.app → **New Project** → **Deploy from GitHub**.
2. Укажите ваш репозиторий с файлами.
3. В разделе **Variables** добавьте переменную `BOT_TOKEN` со значением токена.
4. Railway сам установит зависимости и запустит `python bot.py` (см. `railway.json`).

---

## Проверка
- /start — подсказки
- /bycode A0UJA — пример запроса по коду
- /byname Реакторное здание — пример запроса по названию

Если нужно добавить кнопки, inline-поиск или вынести данные в БД — просто дайте знать.
