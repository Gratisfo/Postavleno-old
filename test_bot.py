import asyncio, re, json, time, functools, datetime, gspread

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, ReplyKeyboardMarkup, \
    Message, ParseMode, ReplyKeyboardRemove
from aiogram import Bot, Dispatcher, types, executor
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from other import *
from wh_json_result import wh_data
from wh_primary import wh_primary
from all_wh import all_wh

from config import api_token_test, admins_user_id
from texts import welcome_message, wh_info, info_message, welcome_old
from ranging_wh import *
from sqlite_users import *
from users import users_info
import logging
logging.basicConfig(level=logging.INFO)

json_file_path = 'admin_.json'

TOKEN_API = api_token_test

bot = Bot(TOKEN_API)
dp = Dispatcher(bot, storage=MemoryStorage())
dp.middleware.setup(LoggingMiddleware())

news_message = ''
start_user_message = ''
post_text = ''

start_status = 'Неактивен'
post_status = 'Неактивен'

new_message_text = 'Разослать пользователям сообщение'
start_message_text = 'Редактировать сообщение после старта'
post_push_text = 'Настроить оповещение о посте'


def rate_limit(limit=1, delay=1):
    def decorator(func):
        last_call = 0

        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            nonlocal last_call
            current_time = time.time()
            elapsed_time = current_time - last_call
            if elapsed_time < delay:
                await asyncio.sleep(delay - elapsed_time)
            last_call = current_time
            return await func(*args, **kwargs)

        return wrapper

    return decorator

async def send_new_message(chat_id):
    # await asyncio.sleep(180)
    url_button = types.InlineKeyboardButton("ПОДПИСАТЬСЯ", url="https://t.me/postavleno")
    keyboard = InlineKeyboardMarkup()
    keyboard.add(url_button)
    await bot.send_message(chat_id, start_user_message, reply_markup=keyboard, disable_web_page_preview=True)


@dp.message_handler(commands=['start'])
@rate_limit(limit=1, delay=1)
async def start(message: Message):
    user = message.from_user
    button_1 = InlineKeyboardButton(text="🔥 Подбор складов 🔥", callback_data="wh_range")
    button_3 = InlineKeyboardButton(text="Исходная таблица", callback_data="fast_wh")
    button_2 = InlineKeyboardButton(text='Топ складов по округам', callback_data='range_fo')
    button_4 = InlineKeyboardButton(text="🗿 Подписаться на канал", url="https://t.me/postavleno")
    keyboard = InlineKeyboardMarkup(row_width=1).add(button_1, button_2, button_3, button_4)

    await message.answer(welcome_old, reply_markup=keyboard, disable_web_page_preview=True)

    data = get_json(json_file_path)
    if start_status == 'Активно' and user.id not in users_info:
        await asyncio.sleep(600)
        await send_new_message(message.chat.id)


@dp.callback_query_handler(text='fast_wh')
@rate_limit(limit=1, delay=1)
async def process_update(callback_query: CallbackQuery):
    file_name = 'Самые быстрые склады.xlsx'
    with open(file_name, 'rb') as file:
        await bot.send_document(callback_query.from_user.id, file)
        data = get_json(json_file_path)
        post_status = data.get('post_status')
        text = data.get('post_text')
        if post_status == 'Активно':
            await asyncio.sleep(1)
            await bot.send_message(callback_query.from_user.id, text, disable_web_page_preview=True)


@dp.message_handler(commands=['info'])
@rate_limit(limit=1, delay=1)
async def help_user(message: Message):
    await message.answer(info_message)


class News(StatesGroup):
    text = State()


class Start(StatesGroup):
    text = State()


class Post(StatesGroup):
    text = State()

news_message = ''
start_user_message = "Бот был полезен?! \nОтлично! В нем скоро появится еще больше крутых функций для селлеров🔥\n\nА самую полезную и актуальную информации по поставкам и не только ты можешь найти в нашем телеграмм-канале \n@postavleno\n\nПодписывайся😎\n\nИ не забывай просить у бота свежие файлы, скорость часто меняется!"
post_text = ''

start_status = 'Неактивен'
post_status = 'Неактивен'

new_message_text = 'Разослать пользователям сообщение'
start_message_text = 'Редактировать сообщение после старта'
post_push_text = 'Настроить оповещение о посте'


@dp.message_handler(commands=['admin_mode'])
async def admin_mode_start(message: types.Message):
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(new_message_text).add(start_message_text).add(post_push_text)
    if message.from_user.id in admins_user_id:
        await message.answer('Выберите действие, которое хотите осуществить', reply_markup=keyboard)


@dp.message_handler(text=new_message_text)
async def add_news_text(message: types.Message):
    await message.answer('Отправьте текст для рассылки пользователям')
    await News.text.set()


@dp.message_handler(state=News.text)
async def process_size(message: Message, state: FSMContext):
    button1 = InlineKeyboardButton(text="Разослать сообщение", callback_data='send_news')
    button2 = InlineKeyboardButton(text="Редактировать текст", callback_data='edit_news')
    keyboard = InlineKeyboardMarkup(row_width=2).add(button1, button2)
    async with state.proxy() as data:
        global news_message
        data['text'] = message.text
        news_message = message.text
    await message.answer(f"Сообщение для рассылки пользователям: \n\n{news_message}. \n\nВыберите действие\n\n"
                         f"Для отмены и перехода в главное меню администратора, вызовите команду /admin_mode",
                         parse_mode=ParseMode.HTML, reply_markup=keyboard, disable_web_page_preview=True)
    await state.finish()


@dp.message_handler(text=start_message_text)
async def add_item(message: Message):
    button1 = InlineKeyboardButton(text="Редактировать текст", callback_data='edit_start')
    button2 = InlineKeyboardButton(text="Изменить статус", callback_data='edit_start_status')
    keyboard = InlineKeyboardMarkup(row_width=2).add(button1, button2)
    if start_user_message == '':
        await message.answer('На данный момент этот текст не настроен\n\n'
                             f'Статус: {start_status}', reply_markup=keyboard)
    else:
        await message.answer(f'Текст для отправки пользователям после запуска бота: \n\n{start_user_message}\n\n '
                             f'Статус: {start_status}', parse_mode=ParseMode.HTML, reply_markup=keyboard, disable_web_page_preview=True)


@dp.message_handler(state=Start.text)
async def process_size(message: Message, state: FSMContext):
    button1 = InlineKeyboardButton(text="Сохранить сообщение", callback_data='save_start')
    button2 = InlineKeyboardButton(text="Редактировать текст", callback_data='edit_start')
    keyboard = InlineKeyboardMarkup(row_width=2).add(button1, button2)
    async with state.proxy() as data:
        global start_user_message
        data['text'] = message.text
        start_user_message = message.text
    await message.answer(f"Сообщение для рассылки пользователям: \n\n{start_user_message}. \n\nВыберите действие\n\n"
                         f"Для отмены и перехода в главное меню администратора, вызовите команду /admin_mode",
                         parse_mode=ParseMode.HTML, reply_markup=keyboard, disable_web_page_preview=True)
    await state.finish()


@dp.message_handler(text=post_push_text)
async def add_item(message: types.Message):
    button1 = InlineKeyboardButton(text="Редактировать текст", callback_data='edit_post')
    button2 = InlineKeyboardButton(text="Изменить статус", callback_data='edit_post_status')
    keyboard = InlineKeyboardMarkup(row_width=2).add(button1, button2)

    if post_text == '':
        await message.answer('На данный момент это сообщение не настроено\n\n'
                             f'Статус: {start_status}', reply_markup=keyboard)
    else:
        await message.answer(f'Сообщение пользователям, которое приходит после таблицы: \n\n{post_text}\n\n '
                             f'Статус: {post_status}', parse_mode=ParseMode.HTML, reply_markup=keyboard, disable_web_page_preview=True)


@dp.message_handler(state=Post.text)
async def process_size(message: types.Message, state: FSMContext):
    button1 = InlineKeyboardButton(text="Сохранить сообщение", callback_data='save_post')
    button2 = InlineKeyboardButton(text="Редактировать текст", callback_data='edit_post')
    keyboard = InlineKeyboardMarkup(row_width=2).add(button1, button2)
    async with state.proxy() as data:
        global post_text
        data['text'] = message.text
        post_text = message.text
    await message.answer(f"Сообщение для рассылки пользователям: \n\n{post_text}. \n\nВыберите действие\n\n"
                         f"Для отмены и перехода в главное меню администратора, вызовите команду /admin_mode",
                         parse_mode=ParseMode.HTML, reply_markup=keyboard, disable_web_page_preview=True)
    await state.finish()



@dp.callback_query_handler()
async def callback_query_keyboard(callback_query: types.CallbackQuery):
    global start_status
    global post_status

    # news
    if callback_query.data == 'send_news':
        for user_id in admins_user_id:
            await bot.send_message(user_id,text=news_message, parse_mode=ParseMode.HTML, disable_web_page_preview=True)

        await bot.send_message(callback_query.from_user.id,
                               'Сообщение успешно отправлено пользователям. '
                               'Для перехода в главное меню администратора, вызовите команду /admin_mode')

    elif callback_query.data == 'edit_news':
        await callback_query.message.answer('Отправьте текст для рассылки пользователям')
        await News.text.set()

    # start
    elif callback_query.data == 'edit_start':
        await callback_query.message.answer('Отправьте стартовый текст для рассылки новым пользователям')
        await Start.text.set()

    elif callback_query.data == 'save_start':
        await callback_query.message.answer('Сообщение сохранено. \n\n '
                                            'Для перехода в главное меню администратора, '
                                            'вызовите команду /admin_mode ')

    elif callback_query.data == 'edit_start_status':
        button1 = InlineKeyboardButton(text="Активно", callback_data='active_start')
        button2 = InlineKeyboardButton(text="Неактивно", callback_data='inactive_start')
        keyboard = InlineKeyboardMarkup(row_width=2).add(button1, button2)

        await callback_query.message.answer('Установите статус отправки сообщения пользователю '
                                            'после первичного использования бота', reply_markup=keyboard)

    elif callback_query.data == 'active_start':
        start_status = 'Активно'
        await callback_query.message.answer(f'Обновленный статус: {start_status} \n\n'
                                            'Для перехода в главное меню администратора, '
                                            'вызовите команду /admin_mode ')

    elif callback_query.data == 'inactive_start':
        start_status = 'Неактивно'
        await callback_query.message.answer(f'Обновленный статус: {start_status} \n\n'
                                            'Для перехода в главное меню администратора, '
                                            'вызовите команду /admin_mode ')

    # post
    elif callback_query.data == 'edit_post':
        await callback_query.message.answer('Отправьте текст для сообщения, которое будет отправляться после таблицы')
        await Post.text.set()


    elif callback_query.data == 'save_post':
        await callback_query.message.answer('Сообщение сохранено. \n\n '
                                            'Для перехода в главное меню администратора, '
                                            'вызовите команду /admin_mode ')

    elif callback_query.data == 'edit_post_status':
        button1 = InlineKeyboardButton(text="Активно", callback_data='active_post')
        button2 = InlineKeyboardButton(text="Неактивно", callback_data='inactive_post')
        keyboard = InlineKeyboardMarkup(row_width=2).add(button1, button2)

        await callback_query.message.answer('Установите статус отправки сообщения пользователю '
                                            'после первичного использования бота', reply_markup=keyboard)

    elif callback_query.data == 'active_post':
        post_status = 'Активно'
        await callback_query.message.answer(f'Обновленный статус: {post_status} \n\n'
                                            'Для перехода в главное меню администратора, '
                                            'вызовите команду /admin_mode ')

    elif callback_query.data == 'inactive_post':
        post_status = 'Неактивно'
        await callback_query.message.answer(f'Обновленный статус: {post_status} \n\n'
                                            'Для перехода в главное меню администратора, '
                                            'вызовите команду /admin_mode ')
        # ранжирование складов
    elif callback_query.data == 'wh_range':
        await callback_query.answer()
        user_id = callback_query.from_user.id
        set_default(user_id, 6)
        text_wh_range = create_wh_text(wh_data[6])  # По умолчанию 6 складов

        button1 = InlineKeyboardButton(text="Изменить кол-во складов", callback_data='edit_wh_num')
        button2 = InlineKeyboardButton(text="Заменить склад", callback_data='edit_wh')
        button3 = InlineKeyboardButton(text="Главное меню", callback_data='main_menu')

        keyboard = InlineKeyboardMarkup(row_width=1).add(button1, button2, button3)
        with open('photo.jpg', 'rb') as image_file:
            await bot.send_photo(callback_query.from_user.id, photo=image_file, caption=text_wh_range,
                                 reply_markup=keyboard, parse_mode=ParseMode.HTML)
    # Замена количества скадов
    elif callback_query.data == 'edit_wh_num':
        await callback_query.answer()
        user_id = callback_query.from_user.id
        update_warehouse_count(user_id, 6)

        text = create_wh_text(
            wh_data[6]) + '\n\n<b>Пожалуйста, выберите необходимое количество складов для поставки. </b>'

        keyboard = wh_buttons(6)
        await bot.send_message(callback_query.from_user.id, text,
                               reply_markup=keyboard, parse_mode=ParseMode.HTML, disable_web_page_preview=True)

    elif callback_query.data.startswith("wh_number"):
        await callback_query.answer()
        user_id = callback_query.from_user.id
        num = int(re.search(r'\d+', callback_query.data).group())
        update_warehouse_count(user_id, num)
        text = create_wh_text(
            wh_data[num]) + '\n\n<b>Пожалуйста, выберите необходимое количество складов для поставки. </b>'

        await callback_query.answer()
        await callback_query.message.edit_text(
            text=text, reply_markup=wh_buttons(num), parse_mode=ParseMode.HTML, disable_web_page_preview=True)

    # Замена склада
    elif callback_query.data == 'edit_wh':
        await callback_query.answer()
        user_id = callback_query.from_user.id

        warehouse_count, deleted_warehouses, last_message_time = get_user_data(user_id)

        text = create_wh_text(wh_data[warehouse_count]) + '\n\n<b>Какой склад заменить?</b>'

        buttons = [InlineKeyboardButton(str(key), callback_data=f"{key}") for key, value in
                   wh_data[warehouse_count].items()]
        cancel_button = InlineKeyboardButton("Отмена", callback_data="wh_range")
        keyboard = InlineKeyboardMarkup(row_width=1).add(*buttons).add(cancel_button)

        try:
            await callback_query.message.edit_text(
                text=text, reply_markup=keyboard, parse_mode=ParseMode.HTML, disable_web_page_preview=True)
        except:
            await callback_query.message.edit_caption(
                caption=text, reply_markup=keyboard, parse_mode=ParseMode.HTML)

    elif callback_query.data in all_wh:
        await callback_query.answer()

        wh_to_delete = callback_query.data
        user_id = callback_query.from_user.id
        current_time = time.time()

        cancel_button = InlineKeyboardButton("Отмена", callback_data="wh_range")

        # Получаем данные из БД
        warehouse_count, deleted_warehouses, last_message_time = get_user_data(user_id)

        if current_time - last_message_time < 2:
            time.sleep(2)

        else:
            print(
                f'У были пользователя удаленные склады: {deleted_warehouses} и добавили {wh_to_delete}, count {warehouse_count}')
            add_deleted_warehouse(user_id, wh_to_delete)
            deleted_warehouses.append(wh_to_delete)
            print('теперь удаленные склады вот такие', deleted_warehouses)
            new_wh = generate_query(warehouse_count, deleted_warehouses)
            print(new_wh, 'пришло такое из базы')

            if new_wh is None and warehouse_count > 1:
                while new_wh is None:
                    warehouse_count -= 1
                    if warehouse_count == 0:
                        break
                    else:

                        new_wh = generate_query(warehouse_count, deleted_warehouses)
                        update_warehouse_count(user_id, warehouse_count)

            print('Новые склады', new_wh)

            try:
                text = create_wh_text(new_wh)
                buttons = [InlineKeyboardButton(str(key), callback_data=f"{key}") for key, value in new_wh.items()]
                keyboard = InlineKeyboardMarkup(row_width=1).add(*buttons).add(cancel_button)
            except:
                text = 'Вы заменили все возможные склады'
                keyboard = InlineKeyboardMarkup(row_width=1).add(cancel_button)

            try:
                await callback_query.message.edit_text(
                    text=text, reply_markup=keyboard, parse_mode=ParseMode.HTML, disable_web_page_preview=True)
            except:
                await callback_query.message.edit_caption(
                    caption=text, reply_markup=keyboard, parse_mode=ParseMode.HTML)


    # Топ по ФО
    elif callback_query.data == 'range_fo':
        await callback_query.answer()
        text = 'Влияние складов на ранжирование в регионе <b>Центральный</b>👈 \n\n'
        buttons = []
        for key in wh_primary:
            value = str(key)
            if value == 'Центральный':
                value = '✅ Центральный'
            buttons.append(InlineKeyboardButton(value, callback_data=f"{key}"))

        for key, value in wh_primary['Центральный'].items():
            text += f'{key}: {int(value)}%\n'

        text += '\n\n<b>Пожалуйста выберите интересующий вас регион.</b>'
        cancel_button = InlineKeyboardButton(text="Главное меню", callback_data='main_menu')
        keyboard = InlineKeyboardMarkup(row_width=2).add(*buttons).add(cancel_button)
        with open('photo_2.jpg', 'rb') as image_file:
            await bot.send_photo(callback_query.from_user.id, photo=image_file, caption=text,
                                 reply_markup=keyboard, parse_mode=ParseMode.HTML)

    elif callback_query.data in wh_primary:
        await callback_query.answer()
        text = f'Влияние складов на ранжирование в регионе <b>{callback_query.data}</b>👈 \n\n'
        buttons = []
        for key in wh_primary:
            value = str(key)
            if value == callback_query.data:
                value = '✅ ' + str(key)
            buttons.append(InlineKeyboardButton(value, callback_data=f"{key}"))

        for key, value in wh_primary[callback_query.data].items():
            text += f'{key}: {int(value)}%\n'
        text += '\n\n<b>Пожалуйста выберите интересующий вас регион.</b>'
        cancel_button = InlineKeyboardButton("Главное меню", callback_data="main_menu")
        keyboard = InlineKeyboardMarkup(row_width=2).add(*buttons).add(cancel_button)
        await callback_query.message.edit_caption(
            caption=text, reply_markup=keyboard, parse_mode=ParseMode.HTML)

    elif callback_query.data == 'main_menu':
        await callback_query.answer()
        button_1 = InlineKeyboardButton(text="🔥 Подбор складов 🔥", callback_data="wh_range")
        button_3 = InlineKeyboardButton(text="Исходная таблица", callback_data="fast_wh")
        button_2 = InlineKeyboardButton(text='Топ складов по округам', callback_data='range_fo')
        button_4 = InlineKeyboardButton(text="🗿 Подписаться на канал", url="https://t.me/postavleno")
        keyboard = InlineKeyboardMarkup(row_width=1).add(button_1, button_2, button_3, button_4)

        await bot.send_message(callback_query.from_user.id, welcome_old,
                               reply_markup=keyboard, parse_mode=ParseMode.HTML, disable_web_page_preview=True)



if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
