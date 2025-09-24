import asyncio
from datetime import datetime

from aiogram.filters import Command, CommandStart
from aiogram.types import Message, BotCommand, CallbackQuery, FSInputFile
from aiogram import Dispatcher, types, Bot, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.state import State

from config import bot_token
from db_rrequests import find_ads, find_ads_today

dp = Dispatcher(storage=MemoryStorage())


async def set_commands(bot: Bot):
    commands = [
        BotCommand(command='start', description="Запустить бота"),
        BotCommand(command='1_hour', description="Объявления за последний час"),
        BotCommand(command='3_hours', description="Объявления за последние 3 часа"),
        BotCommand(command='today', description='Все объявления за сегодня')
    ]
    await bot.set_my_commands(commands)


@dp.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
    await message.answer('Выбери за какой период отправить объявления')


@dp.message(Command('today', '1_hour', '3_hours'))
async def price_command(message: Message, state: FSMContext):
    await state.clear()

    if message.text == '/1_hour':
        ads = find_ads(1)
    elif message.text == '/3_hours':
        ads = find_ads(3)
    else:
        ads = find_ads_today()

    if len(ads) == 0:
        await message.answer('Нет новых объявлений')
    else:
        for ad in ads:
            name, price, metro, link, date_add, payment, time_metro, type_transportation = ad
            dt = datetime.strptime(date_add, "%Y-%m-%d %H:%M:%S")
            formatted_date = dt.strftime("%d.%m.%Y %H:%M")
            text = (
                f"{name}\n"
                f"Аренда: {price} ₽\n"
                f"Оплата при заселении: {payment} ₽\n"
                f"Метро: {metro}, {type_transportation} {time_metro} мин.\n"
                f"Обновлено: {formatted_date}\n"
                f"{link}\n"
            )
            await message.answer(text)
            await asyncio.sleep(1.2)


async def main():
    bot = Bot(token=bot_token)
    await set_commands(bot)
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
