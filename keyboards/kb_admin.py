from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

kb_admin = ReplyKeyboardMarkup(resize_keyboard=True)
add_worker = KeyboardButton('Надати працівнику права')
del_worker = KeyboardButton('Скасувати працівнику права')
kb_admin.add(add_worker, del_worker)