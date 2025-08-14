
# Telegram Explicaciya Bot

### Что делает
Бот ищет наименование по коду и наоборот. Поддерживает:
- `/bycode <КОД>` → наименование
- `/byname <НАИМЕНОВАНИЕ>` → коды
- диалоговый ввод без аргументов
- `/reload` — перечитать список без перезапуска

### Данные
Бот читает список из `explikaciya_mapping.json`. Если его нет — пытается прочитать
`explikaciya_codes_names.csv` (формат: `code,name` в первой строке заголовка).

**JSON может быть в одном из видов**:
1) `{ "code_to_name": {"A0UJA": "Реакторное здание", ...}, "name_to_codes": {"реакторное здание": ["A0UJA", ...]} }`
2) `{ "A0UJA": "Реакторное здание", ... }`

### Запуск на Render
1. Установите переменную окружения `BOT_TOKEN`.
2. Build Command: `pip install -r requirements.txt`
3. Start Command: `python bot.py`

### Обновление списка
- Замените `explikaciya_mapping.json` или `explikaciya_codes_names.csv` и отправьте `/reload` боту.
