import json
from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.types import ContentType, Message, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from create_bot import bot
from google_sheets_integration.main import *
from json_functionality import user_register_status, save_name_to_json
from keyboards.kb_client import kb_client
from google_sheets_integration.main import *


class FSMClient(StatesGroup):
    user_name = State()


# @dp.message_handler(commands=['start'])
async def start_command(message: Message):
    user_status = user_register_status(str(message.from_user.id))
    if user_status['is_id'] and user_status['is_name']:
        await message.answer(text=f'Вітаю, {user_status["name"]}', reply_markup=kb_client)
    elif user_status['is_id'] and not user_status['is_name']:
        await FSMClient.user_name.set()
        await message.answer(text="Введіть прізвище та ім'я", reply_markup=ReplyKeyboardRemove())
    else:
        await message.answer(
            text='У вас немає доступу до бота. Після отримання доступу від адміністратора, натисніть на команду /start',
            reply_markup=ReplyKeyboardRemove())


async def load_name(message: types.Message, state: FSMContext):
    full_name = message.text
    if len(full_name.split()) < 2:
        await message.answer("Введіть прізвище та ім'я через пробіл")
    else:
        await save_name_to_json(str(message.from_user.id), name=full_name)
        await state.finish()

        add_user_to_table(user_name=full_name)
        await message.answer(f"Вітаю, {full_name} можете розпочинати роботу", reply_markup=kb_client)


# @dp.message_handler(Text(equals='Почати роботу'))
async def start_work(message: types.Message):
    print(message)
    await message.answer(text='Ви почали працювати')


# @dp.message_handler(Text(equals='Мої години'))
async def user_hours(message: types.Message):
    await message.answer(text=f'Ви відпрацювали 20 годин!')
    await message.delete()


# @dp.message_handler(Text(equals='Закінчити роботу'))
async def end_work(message: types.Message):
    await message.answer(text=f'Роботу закінчено, ви відпрацювали ... годин!')
    await message.delete()


def register_handlers_client(dp: Dispatcher):
    dp.register_message_handler(start_command, commands=['start'], state=None)
    dp.register_message_handler(load_name, state=FSMClient.user_name)
    dp.register_message_handler(start_work, content_types=['location'])
    dp.register_message_handler(user_hours, Text(equals='Мої години'))
    dp.register_message_handler(end_work, Text(equals='Закінчити роботу'))
