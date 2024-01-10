import gspread
from oauth2client.service_account import ServiceAccountCredentials
from itertools import combinations
from sqlite import *

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


def wh_range(data):
    for county, county_data in data['Counties'].items():
        wh_list = {}
        fo_population = county_data['total_population']

        for region_data in county_data['region'].values():
            region_population = region_data['population']
            best_speed = list(region_data['warehouses'].values())[0]

            # Вычисляем процент заказов с поправкой на население
            orders_pop = region_population / fo_population

            for wh, speed in region_data['warehouses'].items():
                coef = best_speed / speed * orders_pop * 0.4

                if wh not in wh_list:
                    wh_list[wh] = coef
                else:
                    wh_list[wh] += coef
        wh_list = {key: int(value * 100) for key, value in wh_list.items()}
        data["Counties"][county]["wh_range"] = dict(sorted(wh_list.items(), key=lambda item: item[1], reverse=True))

    primary_wh = {key: data['Counties'][key]['wh_range'] for key in data['Counties']}

    with open("/root/bot_wb/wh_primary.py", "w") as file:
        file.write(f"wh_primary = {primary_wh}")
    print('wh primary updated')
    return data


def convert_table_to_json(table):
    result = {}
    counties = {}

    for row in table:
        district, orders, region, population, *priorities = row

        # Создаем словарь для округа если не существует
        if district not in counties:
            counties[district] = {"orders": float(orders), "region": {}}

        # Создаем словарь региона, если он не существует
        if region not in counties[district]["region"]:
            counties[district]["region"][region] = {'population': int(population), 'warehouses': {}}

        # Добавляем приоритеты в словарь регионов
        for priority in priorities:
            if priority == 'нет данных':
                pass
            else:
                priority_name, priority_hours = priority.split(", ")

                priority_hours = int(priority_hours.split(" ч")[0])

                counties[district]["region"][region]["warehouses"][priority_name] = priority_hours

    result["Counties"] = counties
    return result


def add_fo_params(data):
    for county, county_data in data['Counties'].items():
        # Выбираем ФО и входящие в него города
        region_data = county_data['region']

        # Для каждого города добавляем скорость доставки склада 1 приоритета
        region_hours = [list(region_data[city]["warehouses"].values())[0] for city in region_data.keys()]

        # Находим среднюю лучшую скорость по ФО
        avg_speed = sum(region_hours) / len(region_hours)

        # Добавляем каждому ФО новое значение
        data['Counties'][county]['best_speed'] = avg_speed

        # Добавляем каждому ФО количество городов в нем
        data['Counties'][county]['countries_num'] = len(region_hours)

        # Считаем общую численность ФО
        total_population = sum(region_data[city]["population"] for city in region_data)

        # Добавляем каждому ФО суммарное кол-во населения по городам
        data['Counties'][county]['total_population'] = total_population


        # Добавляем каждому ФО суммарное кол-во населения по городам
        data['Counties'][county]['total_population'] = total_population

    # Делаем список всех складов из таблицы
    global all_wh
    all_wh_set = set()
    for county_data in data["Counties"].values():
        for region_data in county_data["region"].values():
            all_wh_set.update(region_data['warehouses'].keys())

    all_wh = list(all_wh_set)


    with open("/root/bot_wb/all_wh.py", "w") as file:
        file.write(f"all_wh = {all_wh}")


    data_result = wh_range(data)

    return data_result


def get_ranging(input_wh, fo_data):
    result = {}

    for county, county_data in fo_data["Counties"].items():

        orders = county_data['orders']
        fo_population = county_data['total_population']

        for region, region_data in county_data['region'].items():

            whs_data = region_data['warehouses']
            best_region_speed = next(iter(whs_data.values()))
            region_population = region_data['population']

            # Вычисляем процент заказов с поправкой на население
            orders_pop = orders * region_population / fo_population

            for wh in whs_data:

                # Проверяем чтобы склад был в поступившем списке
                if wh in list(input_wh):
                    wh_speed = whs_data[wh]

                    # Рассчитываем коэфициент для склада
                    reg_res = best_region_speed / wh_speed * orders_pop * 0.4

                    result.setdefault(wh, 0)
                    result[wh] += reg_res

                    break
    return result


def sum_of_values(dictionary):
    return sum(dictionary.values())


def range_values(result):
    # Находим словарь с самой большой суммой значений
    max_dict = max(result, key=lambda d: sum(d.values()))
    max_dict = {key: round(value, 2) for key, value in max_dict.items()}
    print(f"Лучшая комбинация для {len(max_dict)} скадов", max_dict)
    return max_dict


def get_data():
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
   # credentials = ServiceAccountCredentials.from_json_keyfile_name('bot-postavleno-291d486bd79b.json', scope)
    credentials = ServiceAccountCredentials.from_json_keyfile_dict(json.loads(service_bot), scope)
    gc = gspread.authorize(credentials)
    spreadsheet_url = 'https://docs.google.com/spreadsheets/d/1jw04IYij_hVvnLFv-3ao7otskn5NnXFjDJP7agM9VlQ'
    worksheet = gc.open_by_url(spreadsheet_url).worksheet('data')
    data = worksheet.get_all_values()[1:]
    json_data = convert_table_to_json(data)
    result_data = add_fo_params(json_data)
    return result_data


def ranging_result():
    db_start()

    data = get_data()
    best_comb = {}

    for wh_num in range(1, 10):
        result = [get_ranging(combo, data) for combo in list(combinations(all_wh, wh_num))]
        result = sorted(result, key=sum_of_values, reverse=True)
        create_wh_combs(result, wh_num)
        best_comb[wh_num] = range_values(result)
    rename_db()
    with open("/root/bot_wb/wh_json_result.py", "w") as file:
        file.write(f"wh_data = {best_comb}\n")

    return result



