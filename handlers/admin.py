from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import State, StatesGroup
from config import ADMIN_ID
from json_functionality import add_user_to_json
from keyboards.kb_admin import kb_admin


class FSMAdmin(StatesGroup):
    user_id = State()


async def make_changes_command(message: types.Message):
    if str(message.from_user.id) == ADMIN_ID:
        await message.answer(text='Вітаю, адміністратор!', reply_markup=kb_admin)
    else:
        await message.answer(text='У вас немає прав модератора.')


# @dp.message_handler(Text(equals='Додати нового працівника'), state=None)
async def cm_start(message: types.Message):
    if str(message.from_user.id) == ADMIN_ID:
        await FSMAdmin.user_id.set()
        await message.answer('Напишіть id користувача телеграм.\n'
                             '(Щоб дізнатись id, перешліть будь яке його повідомлення боту @getmyid_bot)')


# @dp.message_handler(state=FSMAdmin.user_id)
async def load_id(message: types.Message, state: FSMContext):
    if str(message.from_user.id) == ADMIN_ID:
        user_id = message.text
        if user_id.isdigit():
            await add_user_to_json(user_id, message)
            await state.finish()
        else:
            await message.answer('id має складатись тільки з цифр, надішліть ще раз.')


# @dp.message_handler(state="*", commands='відміна')
# @dp.message_handler(Text(equals='відміна', ignore_case=True), state='*')
async def cancel_handler(message: types.Message, state: FSMContext):
    if str(message.from_user.id) == ADMIN_ID:
        current_state = await state.get_state()
        if current_state is None:
            return
        await state.finish()
        await message.answer('OK')


def register_handlers_admin(dp: Dispatcher):
    dp.register_message_handler(cm_start, Text(equals='Надати працівнику права'), state=None)
    dp.register_message_handler(cm_start, Text(equals='Скасувати працівнику права'), state=None)
    dp.register_message_handler(cancel_handler, state="*", commands='відміна')
    dp.register_message_handler(cancel_handler, Text(equals='відміна', ignore_case=True), state="*")
    dp.register_message_handler(load_id, state=FSMAdmin.user_id)
    dp.register_message_handler(make_changes_command, commands=['moderator'])
