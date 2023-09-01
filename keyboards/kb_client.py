from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

kb_client = ReplyKeyboardMarkup(resize_keyboard=True)
hours_button = KeyboardButton('Мої години')
start_work_btn = KeyboardButton('Почати роботу')
end_work_btn = KeyboardButton('Закінчити роботу')
kb_client.add(hours_button, start_work_btn, end_work_btn)

kb_lunch = ReplyKeyboardMarkup(resize_keyboard=True)
lunch_yes = KeyboardButton('Так')
lunch_no = KeyboardButton('Ні')
kb_lunch.add(lunch_yes, lunch_no)

kb_location = ReplyKeyboardMarkup(resize_keyboard=True)
send_location = KeyboardButton('Надіслати геолокацію', request_location=True)
kb_location.add(send_location)