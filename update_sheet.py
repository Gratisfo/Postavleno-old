import gspread
from oauth2client.service_account import ServiceAccountCredentials
import datetime
from users import users_info
import sqlite3 as sq

def shit_user(data):
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    credentials = ServiceAccountCredentials.from_json_keyfile_name('bot-postavleno-291d486bd79b.json', scope)
    gc = gspread.authorize(credentials)
    spreadsheet_url = 'https://docs.google.com/spreadsheets/d/1LewXZWCE91ykkwmDKj1hhfCxjCgjGxJkchsOSrNU29U'
    worksheet = gc.open_by_url(spreadsheet_url).worksheet('shit')
    worksheet.append_row(data)


def update_google_sheet(data, status):
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    credentials = ServiceAccountCredentials.from_json_keyfile_name('bot-postavleno-291d486bd79b.json', scope)
    gc = gspread.authorize(credentials)
    spreadsheet_url = 'https://docs.google.com/spreadsheets/d/1LewXZWCE91ykkwmDKj1hhfCxjCgjGxJkchsOSrNU29U'
    worksheet = gc.open_by_url(spreadsheet_url).worksheet('Sheet1')
    if status == 'new':
        print('добавляем нового', data)
        worksheet.append_row(data)
    else:
        print('обновляем старого', data)
        all_values = worksheet.get_all_values()
        row_index = None
        for i, row in enumerate(all_values):
            if str(row[0]) == str(data[0]):
                row_index = i
                print(row_index, 'нашли в табле')
                break

        if row_index is not None:
            worksheet.update_cell(row_index + 1, 2, data[1])
            worksheet.update_cell(row_index + 1, 5, data[2])
            print('обновили таблу')


def append_contact(user_id, first_name, last_name, username, status):
    info = []
    current_datetime = datetime.datetime.now()
    date = current_datetime.strftime('%Y-%m-%d')
    time = current_datetime.strftime('%H:%M:%S')
    try:
        name = first_name + ' ' + last_name
    except:
        name = first_name

    if status == 'new':
        info.extend([user_id, username, date, time, name])
        update_google_sheet(info, 'new')
        users_info[user_id] = {
            'username': username,
            'date': date,
            'time': time,
            'name': name,
            'number': None
        }
    elif users_info[user_id]['username'] is None:
        info.extend([user_id, username, name])
        update_google_sheet(info, 'old')
        users_info[user_id] = {
            'username': username,
            'date': date,
            'time': time,
            'name': name,
            'number': users_info[user_id]['number']
        }

    with open("users.py", "w") as file:
        file.write(f'users_info = {users_info}')



def update_block_users():
    conn = sq.connect('users.db')
    cursor = conn.cursor()

    cursor.execute('''
            SELECT id FROM users_data
            WHERE status = 0 
        ''')
    result = cursor.fetchall()
    print(result, len(result))
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    credentials = ServiceAccountCredentials.from_json_keyfile_name('bot-postavleno-291d486bd79b.json', scope)
    gc = gspread.authorize(credentials)
    spreadsheet_url = 'https://docs.google.com/spreadsheets/d/1LewXZWCE91ykkwmDKj1hhfCxjCgjGxJkchsOSrNU29U'
    worksheet = gc.open_by_url(spreadsheet_url).worksheet('shit')
    worksheet.clear()
    worksheet.update('A1', [[value[0]] for value in result])

