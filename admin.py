import asyncio
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, ReplyKeyboardMarkup, \
    KeyboardButton, ReplyKeyboardRemove, Message, ContentType
from config import api_token_test, admins_user_id
from texts import welcome_message, wh_info, info_message, welcome_old
from aiogram import Bot, Dispatcher, types, executor
from aiogram.contrib.middlewares.logging import LoggingMiddleware
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from users import users_info
import time
import functools
import datetime
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.contrib.fsm_storage.memory import MemoryStorage


TOKEN_API = api_token_test
bot = Bot(TOKEN_API)
dp = Dispatcher(bot, storage=MemoryStorage())
dp.middleware.setup(LoggingMiddleware())


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


@dp.message_handler(commands=['start'])
@rate_limit(limit=1, delay=1)
async def start(message: Message):
    # Получите объект пользователя
    user = message.from_user
    # Получите имя и фамилию пользователя
    first_name = user.first_name
    last_name = user.last_name
    # Отправьте сообщение с именем и фамилией пользователя
    await message.reply(f'Привет, {first_name} {last_name}!')
    # user_id = message.from_user.id
    # if user_id not in users_info:
    #     await message.answer(welcome_message,
    #                          reply_markup=ReplyKeyboardRemove())
    #     keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    #     button = KeyboardButton(text="📲Отправить контакт📲", request_contact=True)
    #     keyboard.add(button)
    #     await message.answer("Нажмите на кнопку ниже для авторизации.", reply_markup=keyboard)
    # else:
    #     keyboard = InlineKeyboardMarkup()
    #     get_file_button = InlineKeyboardButton(text="🔥Самые быстрые склады🔥", callback_data="fast_wh")
    #     subscribe_button = InlineKeyboardButton(text="Подписаться на канал", url="https://t.me/postavleno")
    #     keyboard.row(get_file_button)
    #     keyboard.row(subscribe_button)
    #     await message.answer(welcome_old, reply_markup=keyboard)


@dp.message_handler(content_types=ContentType.CONTACT)
@rate_limit(limit=1, delay=1)
async def process_contact(message: Message):
    user_id = message.from_user.id
    info = []
    contact = message.contact
    phone_number = contact.phone_number
    current_datetime = datetime.datetime.now()
    info.append(user_id)
    info.append(phone_number)
    info.append(current_datetime.strftime('%Y-%m-%d'))
    info.append(current_datetime.strftime('%H:%M:%S'))
    update_google_sheet(info)
    await message.answer("Спасибо за ваш контакт!", reply_markup=types.ReplyKeyboardRemove())

    users_info[user_id] = phone_number
    with open("users.py", "w") as file:
        file.write(f'users_info = {users_info}')
    keyboard = InlineKeyboardMarkup(row_width=2)
    button = InlineKeyboardButton(text="Самые быстрые склады", callback_data='fast_wh')
    keyboard.add(button)
    await message.answer(wh_info, reply_markup=keyboard)


@dp.callback_query_handler(text='fast_wh')
@rate_limit(limit=1, delay=1)
async def process_update(callback_query: CallbackQuery):
    file_name = 'wb.xlsx'
    with open(file_name, 'rb') as file:
        await bot.send_document(callback_query.from_user.id, file)


@dp.message_handler(commands=['info'])
@rate_limit(limit=1, delay=1)
async def help_user(message: Message):
    await message.answer(info_message)


def update_google_sheet(data):
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    credentials = ServiceAccountCredentials.from_json_keyfile_name('bot-postavleno-291d486bd79b.json', scope)
    gc = gspread.authorize(credentials)
    spreadsheet_url = 'https://docs.google.com/spreadsheets/d/1LewXZWCE91ykkwmDKj1hhfCxjCgjGxJkchsOSrNU29U'
    worksheet = gc.open_by_url(spreadsheet_url).worksheet('Sheet1')
    worksheet.append_row(data)


class News(StatesGroup):
    text = State()


class Start(StatesGroup):
    text = State()


class Post(StatesGroup):
    text = State()


news_message = ''
start_user_message = ''
post_text = ''

start_status = 'Неактивен'
post_status = 'Неактивен'

new_message_text = 'Отправить сообщение всем пользователям'
start_message_text = 'Догоняющее сообщение при первом использовании'
post_push_text = 'Сообщение вместе с таблицей'



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
                         reply_markup=keyboard)
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
                             f'Статус: {start_status}', reply_markup=keyboard)


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
                         reply_markup=keyboard)
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
                             f'Статус: {post_status}', reply_markup=keyboard)


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
                         reply_markup=keyboard)
    await state.finish()


@dp.callback_query_handler()
async def callback_query_keyboard(callback_query: types.CallbackQuery):
    global start_status
    global post_status

    # news
    if callback_query.data == 'send_news':
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


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
