import asyncio
import aiohttp
from aiogram import Bot, Dispatcher, types
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import Command
from config import API_TOKEN

# Инициализация бота и диспетчера
bot = Bot(token=API_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()

# Базовый URL вашего FastAPI сервиса
API_BASE_URL = "http://127.0.0.1:8000/api/v1"

# Обработчики команд
@dp.message(Command("start"))
async def start_command(message: types.Message):
    await message.reply("Привет, сделай команду /messages чтобы посмотреть все сообщения и /newmessage если хочешь создать новое")

@dp.message(Command("messages"))
async def list_messages(message: types.Message):
    # Получаем номер страницы из сообщения, если есть
    try:
        _, page = message.text.split(' ', 1)
        page = int(page)
    except ValueError:
        page = 1

    async with aiohttp.ClientSession() as session:
        async with session.get(f"{API_BASE_URL}/messages/?page={page}&limit=10") as resp:
            if resp.status == 200:
                data = await resp.json()
                messages = data['messages']
                total_pages = data['total_pages']
                
                if not messages:
                    await message.reply("Сообщений не найдено")
                else:
                    for msg in messages:
                        await message.reply(f"Автор: {msg['author']}\nСообщение: {msg['text']}")
                    
                    if page < total_pages:
                        await message.reply(f"\nПоказаны сообщения страницы {page}. Чтобы увидеть следующую страницу, используйте /messages {page + 1}")
                    else:
                        await message.reply(f"\nЭто последняя страница сообщений.")
            else:
                await message.reply("Ошибка получения сообщений")

@dp.message(Command("newmessage"))
async def new_message(message: types.Message):
    await message.reply("Напиши сообщение в виде /sendmessage <автор> <сообщение>")

@dp.message(Command("sendmessage"))
async def send_message(message: types.Message):
    try:
        _, author, text = message.text.split(' ', 2)
        async with aiohttp.ClientSession() as session:
            async with session.post(f"{API_BASE_URL}/message/", json={"author": author, "text": text}) as resp:
                if resp.status == 200:
                    await message.reply("Сообщение успешно отправлено")
                else:
                    await message.reply("Ошибка отправки сообщения")
    except ValueError:
        await message.reply("Неправильный формат /sendmessage <автор> <сообщение>")

# Основная функция запуска бота
async def main():
    await dp.start_polling(bot)

# Точка входа в программу
if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
