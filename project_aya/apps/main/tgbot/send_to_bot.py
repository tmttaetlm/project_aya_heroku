import telebot
import sqlite3
from sqlite3 import Error
from crontab import CronTab
from datetime import datetime

bot = telebot.TeleBot('5299933627:AAFadtni2QPlSxeikWyTYNN-DukFGkm_KY0')

def write_query(query, params = {}):
    connection = sqlite3.connect('/home/developer/Code/python/project_aya/db.sqlite3')
    cursor = connection.cursor()
    try:
        cursor.execute(query, params)
        connection.commit()
        #print('Query executed successfully')
    except Error as e:
        print(f"The error '{e}' occurred")

def read_query(query, params = {}):
    connection = sqlite3.connect('/home/developer/Code/python/project_aya/db.sqlite3')
    cursor = connection.cursor()
    result = None
    try:
        cursor.execute(query, params)
        result = cursor.fetchall()
        return result
    except Error as e:
        print(f"The error '{e}' occurred")

now = datetime.now().strftime('%d%m_%H%M')
msg = read_query('select text from main_message where clue = :clue', {'clue': 'on_time_msg|'+now})
users = read_query('select * from main_user where role <> "Админ"', {})
admin = read_query('select chat_id, user, msg_id from main_user where role = "Админ"', {})

text = msg[0][0] + f'\n\n<b>Сообщение создано и отправлено администратором. Если требуется ответ, напишите администратору @{admin[0][1]} напрямую</b>'
for usr in users: bot.send_message(usr[1], text, parse_mode = 'HTML')

write_query('delete from main_message where clue = :clue', {'clue': 'on_time_msg|'+now})

cron = CronTab(user=True)
for job in cron: 
    if job.comment == now:
        cron.remove(job)
        cron.write()

bot.delete_message(admin[0][0], admin[0][2])
bot.send_message(admin[0][0], f'Сообщение, запланированное на {now[0:2]}.{now[2:4]} {now[5:7]}:{now[7:9]} отправлено всем пользователям бота')