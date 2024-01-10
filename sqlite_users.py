import sqlite3


def update_warehouse_count(user_id, new_warehouse_count):
    conn = sqlite3.connect('data.db')
    cursor = conn.cursor()

    cursor.execute('UPDATE users_wh SET warehouse_count = ? WHERE id = ?', (new_warehouse_count, user_id))
    conn.commit()

    conn.close()


# Функция для обновления данных пользователя
def set_default(user_id, warehouse_count):
    conn = sqlite3.connect('data.db') 
    cursor = conn.cursor()

    cursor.execute('SELECT id FROM users_wh WHERE id = ?', (user_id,))
    existing_user = cursor.fetchone()

    if existing_user is not None:
        cursor.execute('UPDATE users_wh SET warehouse_count = ?, deleted_warehouses = ?, last_message_time = ? WHERE id = ?',
                       (warehouse_count, None, None, user_id))

    else:
        cursor.execute('INSERT INTO users_wh (id, warehouse_count, deleted_warehouses, last_message_time) VALUES (?, ?, ?, ?)',
                       (user_id, warehouse_count, None, None))
    conn.commit()
    conn.close()


# Функция для добавления нового склада к списку удаленных складов пользователя
def add_deleted_warehouse(user_id, new_deleted_warehouse):
    conn = sqlite3.connect('data.db')
    cursor = conn.cursor()

    cursor.execute('SELECT deleted_warehouses FROM users_wh WHERE id = ?', (user_id,))
    existing_deleted_warehouses = cursor.fetchone()

    if existing_deleted_warehouses:
        existing_deleted_warehouses = existing_deleted_warehouses[0]
        if existing_deleted_warehouses:
            deleted_warehouses_list = existing_deleted_warehouses.split(', ')
        else:
            deleted_warehouses_list = []
        deleted_warehouses_list.append(new_deleted_warehouse)
        print(deleted_warehouses_list)
        updated_deleted_warehouses = ', '.join(deleted_warehouses_list)

        cursor.execute('UPDATE users_wh SET deleted_warehouses = ? WHERE id = ?', (updated_deleted_warehouses, user_id))
        conn.commit()
    else:
        print(f'Пользователь с ID {user_id} не найден.')

    conn.close()


# Функция для добавления нового склада к списку удаленных складов пользователя
def add_deleted_warehouse(user_id, new_deleted_warehouse):
    conn = sqlite3.connect('data.db')
    cursor = conn.cursor()

    cursor.execute('SELECT deleted_warehouses FROM users_wh WHERE id = ?', (user_id,))
    existing_deleted_warehouses = cursor.fetchone()

    if existing_deleted_warehouses:
        existing_deleted_warehouses = existing_deleted_warehouses[0]
        if existing_deleted_warehouses is not None:
            updated_deleted_warehouses = f'{existing_deleted_warehouses}, {new_deleted_warehouse}'
        else:
            updated_deleted_warehouses = new_deleted_warehouse

        cursor.execute('UPDATE users_wh SET deleted_warehouses = ? WHERE id = ?', (updated_deleted_warehouses, user_id))
        conn.commit()
    else:
        print(f'Пользователь с ID {user_id} не найден.')

    conn.close()


# Функция для получения данных пользователя по ID
def get_user_data(id):
    conn = sqlite3.connect('data.db')  # Замените 'mydatabase.db' на имя вашей базы данных
    cursor = conn.cursor()

    cursor.execute('SELECT warehouse_count, deleted_warehouses, last_message_time FROM users_wh WHERE id = ?', (id,))
    user_data = cursor.fetchone()

    conn.close()

    if user_data:
        wh_count, wh_del, last_time = user_data[0], user_data[1], user_data[2]
        if wh_del is None:
            wh_del = []
        else:
            wh_del = wh_del.split(', ')
        if last_time is None:
            last_time = 0
        return wh_count, wh_del, last_time
    else:
        return None


