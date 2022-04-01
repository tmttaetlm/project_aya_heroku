import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "project_aya.settings")
django.setup()

import telebot
from datetime import datetime
from .models import User, Message

bot = telebot.TeleBot('5299933627:AAFadtni2QPlSxeikWyTYNN-DukFGkm_KY0')

now = datetime.now().strftime('%d%m_%H%M')
msg = Message.objects.get(clue='on_time_msg|'+now)
users = User.objects.exclude(role='Админ')
admin = User.objects.filter(role='Админ')

text = msg[0].text + f'\n\n<b>Сообщение создано и отправлено администратором. Если требуется ответ, напишите администратору @{admin[0][1]} напрямую</b>'
for usr in users: bot.send_message(usr.chat_id, text, parse_mode = 'HTML')

msg.delete()

bot.delete_message(admin[0].chat_id, admin[0].msg_id)
bot.send_message(admin[0].chat_id, f'Сообщение, запланированное на {now[0:2]}.{now[2:4]} {now[5:7]}:{now[7:9]} отправлено всем пользователям бота')