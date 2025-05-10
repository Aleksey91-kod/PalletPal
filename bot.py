import os
import json
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
from aiogram.fsm.storage.memory import MemoryStorage
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()

# Получаем токен из переменных окружения
TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
if not TOKEN:
    raise ValueError("TELEGRAM_BOT_TOKEN не найден в переменных окружения")

bot = Bot(token=TOKEN)
dp = Dispatcher(storage=MemoryStorage())

# URL вашего WebApp на GitHub Pages
WEBAPP_URL = "https://aleksey91-kod.github.io/PalletPal/ModernApp/index.html"

def get_main_menu():
    """Клавиатура с кнопкой WebApp"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text="🚛 Открыть PalletPal",
            web_app=WebAppInfo(url=WEBAPP_URL)
        )]
    ])

@dp.message(Command('start'))
async def start(message: types.Message):
    await message.answer(
        "Добро пожаловать в PalletPal!\n"
        "Нажмите кнопку ниже чтобы открыть мини-приложение:",
        reply_markup=get_main_menu()
    )

@dp.message(F.web_app_data)
async def handle_web_app_data(message: types.Message):
    """Обработка данных из WebApp"""
    try:
        data = json.loads(message.web_app_data.data)
        await message.answer(
            f"📦 Получен заказ:\n"
            f"Тип груза: {data.get('item', 'не указан')}\n"
            f"От: {data.get('from', 'не указано')}\n"
            f"До: {data.get('to', 'не указано')}"
        )
    except Exception as e:
        await message.answer(f"Ошибка: {str(e)}")

@dp.message(Command('help'))
async def help_cmd(message: types.Message):
    await message.answer("Помощь по боту: /start - начало работы")

async def main():
    print("Бот запущен...")
    print(f"Используется токен: {TOKEN[:10]}...")
    print(f"WebApp URL: {WEBAPP_URL}")
    await dp.start_polling(bot)

if __name__ == '__main__':
    import asyncio
    asyncio.run(main())