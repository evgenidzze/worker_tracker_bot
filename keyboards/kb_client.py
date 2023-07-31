from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

kb_client = ReplyKeyboardMarkup(resize_keyboard=True)
hours_button = KeyboardButton('Мої години')
start_work_btn = KeyboardButton('Почати роботу', request_location=True)
end_work_btn = KeyboardButton('Закінчити роботу')
kb_client.add(hours_button, start_work_btn, end_work_btn)