import json
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import math
json_file_path = 'admin.json'


def wh_buttons(num):
    number_buttons = [InlineKeyboardButton(str(i), callback_data=f"wh_number_{i}") for i in range(1, 10)]

    number_buttons[num - 1] = InlineKeyboardButton(f"✅ {num}", callback_data=f"wh_number_{num}")
    add_button = InlineKeyboardButton("Заменить склад", callback_data="edit_wh")
    cancel_button = InlineKeyboardButton("Отмена", callback_data="wh_range")

    keyboard = InlineKeyboardMarkup()
    keyboard.add(*number_buttons)
    keyboard.add(cancel_button, add_button)

    return keyboard


def get_json(json_path):
    try:
        with open(json_path, 'r') as file:
            data = json.load(file)
    except FileNotFoundError:
        data = {}
    return data


def update_json(message, text):
    data = get_json(json_file_path)
    data[message] = text
    with open(json_file_path, 'w') as file:
        json.dump(data, file, indent=4)


def create_wh_text(data):
    text = '<b>При загрузке складов:</b>\n'
    sum_r = 0
    sum_new = 0
    print(data)
    sorted_dict = dict(sorted(data.items(), key=lambda item: item[1], reverse=True))

    print(sorted_dict)
    for key, value in sorted_dict.items():
        new_value = round(value / 0.4, 2)
        text += f'\n{key} - {new_value}% '
        sum_r += value
        sum_new += new_value

    sum_r = round(sum_r, 1)
    sum_new = round(sum_new)

    text += f'\n\nВы получите {sum_r} из 40 возможных процента в ранжировании ' \
                f'или {sum_new} из 100 процентов лучшей скорости доставки. ' \
            f'\n\nИнструкция по использованию бота: https://t.me/postavleno/211'

    return text