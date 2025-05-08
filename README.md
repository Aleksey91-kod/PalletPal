# PalletPal

Система управления заказами для перевозки паллет с интеграцией Telegram бота.

## Функциональность

### Для клиентов:
- Создание заказов на перевозку
- Загрузка документов
- Отслеживание статуса заказа
- Чат с водителем

### Для водителей:
- Просмотр доступных заказов
- Принятие заказов
- Чат с клиентом
- Управление статусом доставки

## Установка

1. Клонируйте репозиторий:
```bash
git clone https://github.com/your-username/PalletPal.git
cd PalletPal
```

2. Создайте виртуальное окружение и установите зависимости:
```bash
python -m venv venv
source venv/bin/activate  # для Linux/Mac
venv\Scripts\activate     # для Windows
pip install -r requirements.txt
```

3. Создайте файл `.env` в корневой директории и добавьте необходимые переменные окружения:
```
TELEGRAM_BOT_TOKEN=your_bot_token
```

4. Запустите сервер:
```bash
python server.py
```

5. В отдельном терминале запустите бота:
```bash
python bot.py
```

## Использование

1. Откройте веб-интерфейс:
   - Для клиентов: http://localhost:5000/customer
   - Для водителей: http://localhost:5000/driver

2. Или используйте Telegram бота:
   - Найдите бота по имени @your_bot_name
   - Отправьте команду /start для начала работы

## Технологии

- Backend: Python, Flask, Flask-SocketIO
- Frontend: HTML, CSS, JavaScript, Bootstrap
- Telegram Bot: python-telegram-bot
- WebSocket для чата
- Загрузка и хранение файлов

## Лицензия

MIT 