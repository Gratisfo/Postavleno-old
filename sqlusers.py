import sqlite3 as sq
import gspread
from oauth2client.service_account import ServiceAccountCredentials


def db_users():
    db = sq.connect('db/users.db')
    cur = db.cursor()
    cur.execute('DROP TABLE IF EXISTS users_data')

    cur.execute('''
        CREATE TABLE IF NOT EXISTS users_data (
            id INTEGER,
            username TEXT,
            date DATE,
            time TIME,
            name TEXT,
            number TEXT,
            status BOOLEAN,
            last_news TEXT
        )
    ''')
    db.commit()

db_users()

def update_google_sheet():
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    credentials = ServiceAccountCredentials.from_json_keyfile_name('bot-postavleno-291d486bd79b.json', scope)
    gc = gspread.authorize(credentials)
    spreadsheet_url = 'https://docs.google.com/spreadsheets/d/1LewXZWCE91ykkwmDKj1hhfCxjCgjGxJkchsOSrNU29U'
    worksheet = gc.open_by_url(spreadsheet_url).worksheet('Sheet1')

    # Получение данных из Google Таблицы
    data = worksheet.get_all_records()

    conn = sq.connect('db/users.db')
    cursor = conn.cursor()

    # Запись данных в базу данных
    for row in data:
        id = row.get('id', None)
        username = row.get('username', None)
        date = row.get('date', None)
        time = row.get('time', None)
        name = row.get('name', None)
        number = row.get('number', None)
        status = row.get('status', None)
        last_news = row.get('last_news', None)
        print(id)
        cursor.execute('''
            INSERT INTO users_data (id, username, date, time, name, number, status, last_news)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (int(id), username, date, time, name, number, status, last_news))

    # Сохранение изменений и закрытие соединений
    conn.commit()
    conn.close()


update_google_sheet()

def shit():
    # Подключение к Google Таблице
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    credentials = ServiceAccountCredentials.from_json_keyfile_name('bot-postavleno-291d486bd79b.json', scope)
    gc = gspread.authorize(credentials)

    spreadsheet_url = 'https://docs.google.com/spreadsheets/d/1LewXZWCE91ykkwmDKj1hhfCxjCgjGxJkchsOSrNU29U'
    worksheet = gc.open_by_url(spreadsheet_url).worksheet('shit')  # Используем "shit" как имя листа

    # Получение данных из Google Таблицы (первый столбец)
    id_column = worksheet.col_values(1)

    # Подключение к базе данных SQLite
    conn = sq.connect('db/users.db')
    cursor = conn.cursor()

    # Обновление записей в базе данных
    for user_id in id_column:  # Пропускаем заголовок (первую строку)
        user_id = int(user_id)  # Преобразуем значение ID пользователя в целое число
        cursor.execute('''
            UPDATE users_data
            SET status = ?, last_news = ?
            WHERE id = ?
        ''', (False, '2023-11-03', user_id))

    # Сохранение изменений и закрытие соединений
    conn.commit()
    conn.close()

shit()
# Подключение к базе данных SQLite
conn = sq.connect('db/users.db')
cursor = conn.cursor()

cursor.execute('''
        SELECT * FROM users_data
        LIMIT 5
    ''')


# Извлекаем результат
print(cursor.fetchone())