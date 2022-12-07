"""Добавление данных в google таблицу"""

import gspread
import datetime


sa = gspread.service_account(filename='service_account.json')
sh = sa.open('python-bot')
wks = sh.worksheet('list')

# data = {'name': 'Роберт', 'business': 'Моторные лодки', 'stream': 'No', 'state_of_business': 'Fire', 'fire_state': 'Разобрать на стриме', 'request': 'Спагетти', 'contact': '79624133136', 'contact_id': 172457394, 'contact_name': 'Rufat', 'contact_lastname': None, 'contact_nickname': '@Kazykan'}

def data_time() -> str:
    now = datetime.datetime.now()
    return now.strftime('%d.%m.%Y %H:%M')


def adjustment_data(data: dict) -> list:
    transaction = []
    for k, v in data.items():
        transaction.append(v)
    while len(transaction) < 11:
        transaction.insert(4, None)
    transaction.append(data_time())
    return transaction

def add_to_google_excel(data: dict) -> bool:
    wks.append_row(adjustment_data(data=data))
    return True
