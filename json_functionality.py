import json


def user_register_status(user_id: str) -> dict:
    with open('users.json', 'r+') as file:
        file_data = json.load(file)
        users = file_data['users']
        register_status = {'is_id': False, 'is_name': False}

        if user_id in users:
            register_status['is_id'] = True
            register_status['is_name'] = bool(users[user_id])
            if register_status['is_name']:
                register_status['name'] = users[user_id]
            return register_status
        return register_status


async def add_user_to_json(user_id, message):
    with open('users.json', 'r+') as file:
        file_data = json.load(file)
        if user_id in file_data['users']:
            await message.answer(text=f'У користувача з id: {user_id} вже є доступ.')
        else:
            file_data['users'][user_id] = ""
            file.seek(0)
            json.dump(file_data, file, indent=4)
            await message.answer(text=f'Ви надали доступ користувачу з id: {user_id}')

async def save_name_to_json(user_id, name):
    with open('users.json', 'r+') as file:
        file_data = json.load(file)
        file_data['users'][user_id] = name
        print(name)
        file.seek(0)
        json.dump(file_data, file, indent=4)
