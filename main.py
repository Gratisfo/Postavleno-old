import requests
import json
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from data import regions
from wh_info import unique_wh
import datetime
import urllib.parse
from ranging_wh import *

rows_for_seeet = []

service_bot = '''{
  "type": "service_account",
  "project_id": "bot-postavleno",
  "private_key_id": "291d486bd79b4a8f160eb58e6509dc1d39e47df9",
  "private_key": "-----BEGIN PRIVATE KEY-----\\nMIIEvAIBADANBgkqhkiG9w0BAQEFAASCBKYwggSiAgEAAoIBAQCvcA1dugB+5lO4\\nZ+SdUhwsgylO+lCOVxxzo4Vsvj3nWu0kB9ENh+UVRqs12cijaPUEvfHleK/RPoCY\\nPPu07LB1mEsMKKd9vVpSERrZq+NXPyi2fozgGEbDn6YExkmGLIR+GDu6hX/Wherg\\nuFdw8+517CSExOYhoBv8DynEBs+uazytcA78DAuw50wC38hyJTs/lZK0QhOmqiuG\\nnwAE4vVaB/b+2yj9AH49ZG2/f+QzMErxu+kauu/NMLJK6eKotBwvGljQKpfP5KXe\\n8DkZ/D3m8aKmzGu0z+B6evjxxjPcOgk1fYRxmkiaJ4Hr/hGZtSnsFopoSXn4Fe7u\\nK0r/oFOTAgMBAAECggEABju0dd6McvXLBrPGRyKqNpioaJJzN0N4EtG+BVmTCHvO\\nDigq8NChvopGvgCRZODvR65aAF2z3Xrbhc0w4kJAmMUC8ZkmLk0CfwT1j8NQLgLj\\n9uvzJGkoZn3vH59N8HL3eCVzRdLFcoFKkZZrIOvBzrXHrGH0jUBLjj6ZrMnTKi69\\nJuCmUilfEkt78fmJ+me4t/AJk4tEo2a2Ssb/uMwbz3uMwCHeOE2lly/hyyTwkgxr\\nYRu0NaGitEzF98on0lTqjFYMFRmm4wObUO+jmEWTKNUfryDbLqeCt9OuU8liiPO9\\nQKlhls5JwrQN6mfkbPmsqlu7ZonXuzThJRZ5YIwfQQKBgQDXoq9MRkfgZijGDzbk\\nVK3yYeicndy+BCEwYSH1pa1ZMs8VdFR1lE2e06a81m0vpIrDZr7lAx0i+R45349U\\nQXFtUkQvPm1wZK3KEUQ+8zI9MOoimzx4n2TuV2Zk4C+stb7X6lcPfntn7SKMC38u\\nqha9hCpThLOw3Ts0Jc/nDo2hQQKBgQDQRxP3AhmRhQ/2wb9vMqmt8Kre74xmG4rw\\nUXz8Ul1lqrpsDEy4/0dqggqK7C5G8kFTQy/iW7ADegg3YbhhKeL94hpyAT/STjC4\\nc8ySUjKQsLiPWrdUYZYcs9SFLNSOCiQYkUdNS4cKWEZAwHf6iHtySMPyea8nC4Fc\\n82LezK6r0wKBgHymMicpSUtSQqebC+QZfyPprQk7x+qfgH/y5iqVxwsU79g7EseV\\nHvl855mpahxsRTqHHjpL/n/E+dACh1vxKJxFPd0BfUnHKR7xtD2fX583s2Cl0+L2\\nYOXV5/7QCT8RIGy3rfPq7XM6BQpnavGSqOqMh9sXjrfiauLOKMwsAXsBAoGAOcXt\\nmM/hTcdONVFrC6pO/OvMSgjCtjQfpyfDdq5WL/Rav8vtoEdXhQjLadu3voBGdJUn\\nfC+YtG4uR0Z5AaK/z1LfqQ4FqQ19YDzm2xOn6RDMMR+lyOdE33NWmRZlY30WpCXw\\nVFWGAO2Zly6MWVdwfrQGfoUYe8kqOiFdJJY8QXcCgYApYGjTmwG55Sg4OSmpfvVC\\nwB0Japv9vg5lFeerfJPnwzD7E/7y8JsCVcjftKmKYrFQGjHLw7xPI8zr4mxhx0z6\\n3dY4oU0Q22OCupYmGH6PTB8GBx+H5oB5boHPU3e0JQ+pbFuZLdXXZV7ff4MU1XfS\\nvKrJXaVRz86449v3/sbw2w==\\n-----END PRIVATE KEY-----\\n",
  "client_email": "bot-wb@bot-postavleno.iam.gserviceaccount.com",
  "client_id": "102472724797142835762",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/bot-wb%40bot-postavleno.iam.gserviceaccount.com",
  "universe_domain": "googleapis.com"
}'''


def top_wh_dest(dict_wh, dest):
    sorted_dict = dict(sorted(dict_wh.items(), key=lambda item: item[1]))
    top_15 = {key: sorted_dict[key] for key in list(sorted_dict)[:15]}
    dest_row = [regions[int(dest)]]
    print('dest_row', dest_row)
    for wh_id, hours in top_15.items():
        ready_wh = filtered_dict[wh_id] #.strip()
        print('ready wh', ready_wh)

        wh_time = f'{ready_wh}, {hours} ч'
        dest_row.append(wh_time)

    if len(dest_row) < 16:
        nan_num = 16 - len(dest_row)
        dest_row.extend(['нет данных'] * nan_num)
    print(f"получили такую строку для {dest}: \n{dest_row}")
    return dest_row


def get_wh(card_id, dest):
    response = requests.get(
        f'https://card.wb.ru/cards/detail?appType=1&curr=rub&'
        f'dest={dest}&regions=80,38,83,4,64,33,68,70,30,40,86,69,1,31,66,22,110,48,114&'
        f'spp=0&nm={card_id}',
    )

    warehouses = {}
    data_products = json.loads(response.text)

    print(f'формируем словарь складов для {card_id} регион{dest}')
    for product in data_products["data"]["products"]:
        for size in product["sizes"]:
            wh = size.get("wh")
            time1 = size.get("time1")
            time2 = size.get("time2")
            try:
                time = time1 + time2
                if wh not in warehouses and wh in unique_wh:
                    warehouses[int(wh)] = time
            except:
                pass
    print(f'Это словарь котрый получился с карточки {card_id} и региона {regions[dest]}', warehouses)
    return warehouses


def get_search_result(product, dest, limit):
    product_name = urllib.parse.quote(product, encoding='utf-8')
    response = requests.get(
        f'https://search.wb.ru/exactmatch/ru/common/v4/search?TestGroup=no_test&TestID=no_test&appType=1&'
        f'curr=rub&dest={dest}&query={product_name}&'
        f'regions=80,38,83,4,64,33,68,70,30,40,86,69,1,31,66,22,110,48,114&'
        f'resultset=catalog&sort=popular&spp=0&suppressSpellcheck=false&limit={limit}',
    )
    return response


def get_info(dest, products_dict):
    wh_dict = {}
    responses = [get_search_result(product, dest, products_dict[product]) for product in products_dict]

    for response in responses:
        try:
            cards_info = json.loads(response.text)
            cards_ids = [card["id"] for card in cards_info["data"]["products"]]
            # достаем склады из каждой карточки товара
            print('Начинаем доставать склады')
            i = 0
            for card_id in cards_ids:
                i += 1
                print(f'{i} карточка: {card_id}')
                update_wh = get_wh(card_id, dest)
                wh_dict.update(update_wh)
            print(f"Отправили {dest} на формирование строки. Сечйас в словаре {len(wh_dict)} складов")
        except:
            print('Возникала ошибка', dest)

    result = top_wh_dest(wh_dict, dest)
    return result


def get_google_sheet(sheet_name):
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    credentials = ServiceAccountCredentials.from_json_keyfile_dict(json.loads(service_bot), scope)
    gc = gspread.authorize(credentials)
    # откроем таблицу по URL
    spreadsheet_url = 'https://docs.google.com/spreadsheets/d/1jw04IYij_hVvnLFv-3ao7otskn5NnXFjDJP7agM9VlQ'
    worksheet = gc.open_by_url(spreadsheet_url).worksheet(sheet_name)
    return worksheet


def update_google_sheet(data):
    worksheet = get_google_sheet('sheet1')
    worksheet.clear()
    # запись данных в Google Таблицу
    worksheet.update("A1", data)
    current_datetime = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    worksheet.update("S1", current_datetime)


def download_sheet():
    url = 'https://docs.google.com/spreadsheets/d/1jw04IYij_hVvnLFv-3ao7otskn5NnXFjDJP7agM9VlQ/export?format=xlsx'
    response = requests.get(url)
    if response.status_code == 200:
        with open('/root/bot_wb/Самые быстрые склады.xlsx', 'wb') as file:
            file.write(response.content)
        print('Файл успешно скачан и сохранен как "Самые быстрые склады.xlsx".')
    else:
        print('Не удалось скачать файл.')


def update_wh():
    url = 'https://www.wildberries.ru/webapi/spa/product/deliveryinfo'
    response = requests.get(url)
    data = json.loads(response.text)
    store_data = {}
    for store in data['value']['times']:
        store_id = store['storeId']
        store_name = store['storeName']
        if store_name == 'Екатеринбург 2 WB':
            store_name = 'Перспективный WB'
        if store_name == 'Екатеринбург WB':
            store_name = 'Испытателей WB'
        if store_name == 'Санкт-Петербург WB':
            store_name = 'Уткина Заводь WB'
        if store_name == 'Алексин WB':
            store_name = 'Алексин (Тула) WB'

        store_data[store_id] = store_name

    global filtered_dict
    filtered_dict = {key: value for key, value in store_data.items() if 'WB' in value}
    for key in filtered_dict:
        filtered_dict[key] = filtered_dict[key].replace(" WB", "")
    with open("wh_info.py", "w") as file:
        file.write(f'unique_wh = {filtered_dict}')



if __name__ == '__main__':
    update_wh()
    regions_dest = list(regions.keys())
    products = {'гель для душа': 100, 'футболка': 10}
    data = [get_info(region, products) for region in regions_dest]
    update_google_sheet(data)
    download_sheet()


















