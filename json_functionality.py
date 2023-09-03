import json


def user_register_status(user_id: str) -> dict:
    with open('users.json', 'r+', encoding='utf-8') as file:
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


async def save_user_id_to_json(user_id, message):
    with open('users.json', 'r+', encoding='utf-8') as file:
        file_data = json.load(file)
        if user_id in file_data['users']:
            await message.answer(text=f'У користувача з id: {user_id} вже є доступ.')
        else:
            file_data['users'][user_id] = ""
            file.seek(0)
            json.dump(file_data, file, indent=4)
            await message.answer(text=f'Ви надали доступ користувачу з id: {user_id}')


async def remove_user_id_from_json(user_id, message):
    with open('users.json', 'r', encoding='utf-8') as file:
        file_data = json.load(file)

    if user_id in file_data['users']:
        print(file_data)
        del file_data['users'][user_id]

        with open('users.json', 'w', encoding='utf-8') as file:
            json.dump(file_data, file, indent=4, ensure_ascii=False)

        await message.answer(text=f'Ви скасували права користувачу з id: {user_id}')
    else:
        await message.answer(text=f'Користувача з таким id не існує')


async def save_name_to_json(user_id, name):
    with open('users.json', 'r+', encoding='utf-8') as file:
        file_data = json.load(file)
        file_data['users'][str(user_id)] = name  # Переконайтесь, що user_id - рядок
        file.seek(0)
        json.dump(file_data, file, indent=4, ensure_ascii=False)
        file.truncate()


async def get_name_by_id(user_id):
    with open('users.json', 'r+', encoding='utf-8') as file:
        file_data = json.load(file)
        return file_data['users'][user_id]


def get_all_user_names():
    with open('users.json', 'r', encoding='utf-8') as file:
        file_data = json.load(file)
        user_names = [[name] for name in file_data['users'].values() if name]
        return user_names

def get_all_users():
    with open('users.json', 'r', encoding='utf-8') as file:
        file_data = json.load(file)
        users = "\n".join([f"{name} - `{id}`" if name else f"Без імені - `{id}`" for id, name in file_data['users'].items()])
        return users
