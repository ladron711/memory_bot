import os
import aiohttp
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher.middlewares import BaseMiddleware
from aiogram.dispatcher.handler import CancelHandler
from aiogram.types import ReplyKeyboardRemove
from aiogram.contrib.fsm_storage.memory import MemoryStorage

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from keyboards import category_keyboard, mood_keyboard, starting_keyboard

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
)


BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN is not set in environment variables")
    logging.error("BOT_TOKEN is not set in environment variables") 

ALLOWED_ID = int(os.getenv("ALLOWED_ID"))
API_URL = os.getenv("API_URL")
API_URL_BASE = os.getenv("API_URL_BASE")

class AccessMiddleware(BaseMiddleware):
    async def on_pre_process_message(self, message: types.Message, data: dict):
        if message.from_user.id != ALLOWED_ID:
            raise CancelHandler()

bot = Bot(token=BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)
dp.middleware.setup(AccessMiddleware())

class DiaryStates(StatesGroup):
    category = State()
    mood = State()
    condition = State()
    content = State()

@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    
    await message.answer("Ready to get your memories", reply_markup=starting_keyboard)

@dp.message_handler(lambda message: message.text == "cancel", state='*')
@dp.message_handler(commands=['cancel'], state='*')
async def cancel_handler(message: types.Message, state: FSMContext):
    await state.finish()
    logging.info("User cancelled the entry")
    await message.answer("Entry cancelled", reply_markup=starting_keyboard)

@dp.message_handler(lambda message: message.text == "add")
async def start_diary(message: types.Message):
   
    await message.answer("choose category", reply_markup=category_keyboard)
    await DiaryStates.category.set()

@dp.message_handler(state=DiaryStates.category)
async def get_category(message: types.Message, state: FSMContext):

    allowed = ["работа", "семья", "учеба", "спорт", "отдых", "прочее"]
    if message.text not in allowed:
        await message.answer("choose category from keyboard")
        return 
     
    await state.update_data(category=message.text)
    await message.answer("choose mood", reply_markup=mood_keyboard)
    await DiaryStates.mood.set()

@dp.message_handler(state=DiaryStates.mood)
async def get_mood(message: types.Message, state: FSMContext):
    mood_map = {
        "😊": "позитивное",
        "😐": "нейтральное",
        "😞": "отрицательное"
    }
    if message.text not in mood_map:
        await message.answer("choose mood from keyboard")
        return
    await state.update_data(mood=mood_map[message.text])
    await message.answer("write physical condition", reply_markup=ReplyKeyboardRemove())
    await DiaryStates.condition.set()

@dp.message_handler(state=DiaryStates.condition)
async def get_condition(message: types.Message, state: FSMContext):
    await state.update_data(condition=message.text)
    await message.answer("write your comment")
    await DiaryStates.content.set()

@dp.message_handler(state=DiaryStates.content)
async def get_content(message: types.Message, state: FSMContext):

    await state.update_data(content=message.text)

    user_data = await state.get_data()
    data = {
        "telegram_id": message.from_user.id,
        "username": message.from_user.username,
        "category": user_data.get("category"),
        "mood": user_data.get("mood"),
        "physical_condition": user_data.get("condition"),
        "content": user_data.get("content"),
    }

    try:
        async with aiohttp.ClientSession() as session:
            logging.info("sending data to backend")
            async with session.post(API_URL, json=data) as response:
                if response.status == 201:
                    logging.info(f"Status: {response.status}")
                    await message.answer("Successfully saved", reply_markup=starting_keyboard)
                else:
                    logging.error(f"Failed. Status: {response.status}")
                    await message.answer("Failed", reply_markup=starting_keyboard)
    except Exception as e:
        logging.exception(f"Error occurred while sending data: {e}")
        await message.answer(f"An error occurred: {str(e)}")

    await state.finish()

@dp.errors_handler()
async def global_error_handler(update, exception):
    logging.exception(f"Update caused error: {exception}")
    await bot.send_message(chat_id=ALLOWED_ID, text=f"Error: {str(exception)}")
    return True


async def send_analysis(analysis_type: str):
    async with aiohttp.ClientSession() as session:
        async with session.post(
            API_URL_BASE,
            json={"type": analysis_type, "telegram_id": ALLOWED_ID}
        ) as response:
            if response.status == 200:
                data = await response.json()
                await bot.send_message(
                    chat_id=ALLOWED_ID,
                    text=data["content"]
                )
            else:
                await bot.send_message(
                    chat_id=ALLOWED_ID,
                    text="Ошибка при получении анализа"
                )

async def send_reminder(text: str):
    await bot.send_message(chat_id=ALLOWED_ID, text=text, reply_markup=starting_keyboard)

scheduler = AsyncIOScheduler(timezone="Asia/Almaty")
scheduler.add_job(send_reminder, 'cron', hour=9, minute=15, kwargs={'text': "Good mornong! How did you sleep?"})
scheduler.add_job(send_reminder, 'cron', hour=15, minute=15, kwargs={'text': "How's your day going?"})
scheduler.add_job(send_reminder, 'cron', hour=21, minute=30, kwargs={'text': "Good evening! How was your day?"})
scheduler.add_job(send_analysis, 'cron', hour=22, minute=10, kwargs={'analysis_type': 'daily'})
scheduler.add_job(send_analysis, 'cron', hour=22, minute=15, day_of_week='sun', kwargs={'analysis_type': 'weekly'})
scheduler.add_job(send_analysis, 'cron', hour=21, minute=0, day='1', kwargs={'analysis_type': 'monthly'})


async def on_startup(dp):
    scheduler.start()
    await bot.send_message(chat_id=ALLOWED_ID, text="Bot started")

async def on_shutdown(dp):
    await bot.send_message(chat_id=ALLOWED_ID, text="Bot stopped")


if __name__ == '__main__':
    logging.info("Starting bot...")
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup, on_shutdown=on_shutdown)
    