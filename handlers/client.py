import datetime
from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.types import Message, ReplyKeyboardRemove

from config import GROUP_ID
from create_bot import bot
from google_mao_api import get_static_map_image
from json_functionality import user_register_status, save_name_to_json, get_name_by_id
from keyboards.kb_client import kb_client, kb_location
from google_sheets_integration.main import add_user_to_table, gs


class FSMClient(StatesGroup):
    user_name = State()
    start_location = State()
    end_location = State()


start_work_dict = {}
lunch_break_status = {}


# /start визначає чи є доступ у юзера до бота, якщо так то записує ім'я
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


# Приймає введене ім'я та записує у json
async def load_name(message: types.Message, state: FSMContext):
    full_name = message.text
    if len(full_name.split()) < 2:
        await message.answer("Введіть прізвище та ім'я через пробіл")
    else:
        await state.finish()

        add_user_to_table(user_name=full_name)
        await save_name_to_json(str(message.from_user.id), name=full_name)

        await message.answer(f"Вітаю, {full_name} можете розпочинати роботу", reply_markup=kb_client)


# Реагує на "Почати роботу"
async def start_work(message: types.Message):
    # gs.create_month_table()
    user_id = str(message.from_user.id)
    if user_register_status(user_id)['is_name']:
        if user_id in start_work_dict:
            await message.answer(text='Ви вже почали робочий день.')
        else:
            await FSMClient.start_location.set()
            await message.answer(text='Поділіться геолокацією, щоб почати роботу.', reply_markup=kb_location)
    else:
        await message.answer(text='Ви не зареєстровані.')


# надсилає гео в групу і зберігає dict - {'user_id': 'start_time'}
async def send_start_location(message: types.Message, state: FSMContext):
    await state.finish()
    lat, long = message.location['latitude'], message.location['longitude']
    user_id = str(message.from_user.id)
    name = await get_name_by_id(user_id)

    start_time = datetime.datetime.now()
    start_work_dict[user_id] = start_time

    await bot.send_photo(chat_id=GROUP_ID, photo=get_static_map_image(lat, long),
                         caption=f"{name} почав роботу.")
    await message.answer(text='Ви почали робочий день.', reply_markup=kb_client)


# Реагує на 'Закінчити роботу', надсилає гео та має відняти поточний час від start_time та записати у sheet
async def end_work(message: types.Message, state: FSMContext):
    user_id = str(message.from_user.id)

    if user_id not in start_work_dict:
        await message.answer(text='Щоб закінчити роботу, спочатку її потрібно почати)')
    else:
        await FSMClient.end_location.set()
        await message.answer(text='Поділіться геолокацією, щоб закінчити роботу.', reply_markup=kb_location)


async def send_end_location(message: types.Message, state: FSMContext):
    await state.finish()
    user_id = str(message.from_user.id)
    lat, long = message.location['latitude'], message.location['longitude']
    name = await get_name_by_id(user_id)

    end_time = datetime.datetime.now()
    worked_time = end_time - start_work_dict[user_id]  # відпрацьований час невідформатований
    hours = worked_time.seconds // 3600
    minutes = (worked_time.seconds % 3600) // 60
    current_month_year = f"{datetime.datetime.now().strftime('%B')} {datetime.datetime.now().strftime('%Y')}"

    if current_month_year not in gs.get_sheets():
        gs.create_month_table()
    try:
        old_hours, old_minutes = gs.get_work_hours(user_name=name).split(':')
    except TypeError:
        old_hours, old_minutes = 0, 0
        print('no data in cell')

    new_time = datetime.timedelta(hours=hours, minutes=minutes)
    old_time = datetime.timedelta(hours=int(old_hours), minutes=int(old_minutes))
    result_time = old_time + new_time

    result_hours = result_time.seconds // 3600
    result_minutes = str(((result_time.seconds % 3600) // 60) + 5).zfill(
        2)  # хвилини < 10 додаються як 1, 2 без нуля, не сумуються в таблиці, зробити 01

    gs.add_work_hours(user_name=name, work_time=f"{result_hours}:{result_minutes}")

    await message.answer(text=f'Роботу закінчено, ви відпрацювали {result_hours} годин, {int(result_minutes)}хв!',
                         reply_markup=kb_client)
    await bot.send_photo(chat_id=GROUP_ID, photo=get_static_map_image(lat, long),
                         caption=f'{name} закінчив роботу.')
    del start_work_dict[user_id]

    if user_id in lunch_break_status:
        pass


# @dp.message_handler(Text(equals='Мої години'))
async def user_hours(message: types.Message):
    user_id = str(message.from_user.id)
    name = await get_name_by_id(user_id)
    worked_hours = gs.get_month_hours(name)
    hours, minutes = str(worked_hours).split(':')
    await message.answer(text=f'Цього місяця ви відпрацювали {hours} годин {int(minutes)} хвилин!')


def register_handlers_client(dp: Dispatcher):
    dp.register_message_handler(start_command, commands=['start'], state=None)
    dp.register_message_handler(load_name, state=FSMClient.user_name)

    dp.register_message_handler(start_work, Text(equals='Почати роботу'), state=None)
    dp.register_message_handler(send_start_location, content_types=['location'], state=FSMClient.start_location)

    dp.register_message_handler(end_work, Text(equals='Закінчити роботу'))
    dp.register_message_handler(send_end_location, content_types=['location'], state=FSMClient.end_location)

    dp.register_message_handler(user_hours, Text(equals='Мої години'))
