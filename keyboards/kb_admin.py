from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

kb_admin = ReplyKeyboardMarkup(resize_keyboard=True)
add_worker = KeyboardButton('Додати працівника')
del_worker = KeyboardButton('Видалити працівника')
cancel = KeyboardButton('Відміна')
kb_admin.add(add_worker, del_worker, cancel)