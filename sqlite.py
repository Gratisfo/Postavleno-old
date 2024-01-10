import sqlite3 as sq
import json
import os
import datetime


def db_start():
    db = sq.connect('data_new.db')
    cur = db.cursor()
    cur.execute('DROP TABLE IF EXISTS wh_combination')

    cur.execute('CREATE TABLE IF NOT EXISTS wh_combination(id INTEGER PRIMARY KEY, combination TEXT, number INTEGER)')
    cur.execute('''
            CREATE TABLE IF NOT EXISTS users_wh (
                id INTEGER PRIMARY KEY,
                warehouse_count INTEGER,
                deleted_warehouses TEXT,
                last_message_time TEXT
            )
        ''')
    db.commit()


def db_users():
    db = sq.connect('data_new.db')
    cur = db.cursor()

    cur.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER,
            username TEXT,
            date DATE,
            time TIME,
            name TEXT,
            number TEXT,
            PRIMARY KEY (id)
        )
    ''')
    db.commit()


def create_wh_combs(combinations, num):
    db = sq.connect('data_new.db')
    cur = db.cursor()
    values = [(str(combination), num) for combination in combinations]
    cur.executemany("INSERT INTO wh_combination (combination, number) VALUES (?, ?)", values)
    db.commit()


def rename_db():
    old_db_name = 'data_new.db'
    new_db_name = 'data.db'

    if os.path.exists(old_db_name):
        os.rename(old_db_name, new_db_name)
        print(f"База данных переименована из {old_db_name} в {new_db_name}")
    else:
        print(f"База данных {old_db_name} не найдена")


def generate_query(number, keywords, wh_stay=None):
    db = sq.connect('data.db')
    cur = db.cursor()
    # Формируем часть SQL-запроса для ключей
    conditions1 = [f"combination NOT LIKE '%{keyword}%'" for keyword in keywords]
    # conditions2 = []
    #
    # if wh_stay:
    #     conditions2 = [f"combination LIKE '%{wh}%'" for wh in wh_stay]
    #
    # # Собираем условия вместе с использованием оператора AND
    #     conditions_sql = " AND ".join(conditions1) + " AND " + " AND ".join(conditions2)
    # else:
    #     conditions_sql = " AND ".join(conditions1)

    conditions_sql = " AND ".join(conditions1)


    # Формируем полный SQL-запрос с учетом number и условий по ключам
    query = f"SELECT combination FROM wh_combination WHERE number = {number} AND {conditions_sql} LIMIT 1"


    # Выполняем запрос
    cur.execute(query)

    # Извлекаем результат
    result = cur.fetchone()

    # Закрываем соединение
    db.close()
    print(result)

    if result:
        data_dict = json.loads(result[0].replace("'", '"'))
        return data_dict
    else:
        print('else none')
        return None


def db_new_user(user_id, username, name):
    current_datetime = datetime.datetime.now()
    date = current_datetime.strftime('%Y-%m-%d')
    time = current_datetime.strftime('%H:%M:%S')
    db = sq.connect('users.db')
    cur = db.cursor()
    cur.execute('''
               INSERT INTO users_data (id, username, date, time, name, number, status, last_news)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)
           ''', (int(user_id), username, date, time, name, None, None, None))

    # Сохранение изменений и закрытие соединений
    db.commit()
    db.close()

