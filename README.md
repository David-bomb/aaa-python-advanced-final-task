# aaa-python-advanced-final-task

## About

Здесь реализован простой TG-бот для игры в крестики-нолики БЕЗ мультиплеера. 

Если надо, можете писать мне в MM, чтобы я выслал вам ключ для бота (его username: @aaa_game_bot)

## Алгоритм запуска

1) Создание окружения
```bash
python -m venv venv
```

2) Активация окружения
   
Для Linux/MacOS
```bash
source venv/bin/activate
```

Для Windows
```bash
venv\scripts\activate
```

3) Установка зависимостей

```bash
pip install -r requirements.txt
```

4) Запуск

Тесты
```bash
python -m pytest test_game_logic.py -v
```

Бот
```bash
python bot.py
```



