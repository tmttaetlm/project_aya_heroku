import sys, os
import django
sys.path.append('/home/Yerdos/project_aya') 
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "project_aya.settings")
django.setup()
from django.conf import settings

import telebot
from datetime import datetime
from main.models import User, Message

bot = telebot.TeleBot(settings.TELEGRAM_TOKEN)

now = datetime.now().strftime('%d%m_%H%M')
try:
    msg = Message.objects.get(clue='on_time_msg|'+now)
    users = User.objects.exclude(role='Админ')
    admin = User.objects.filter(role='Админ')

    print(f'Сообщение {msg.id} отправлено')

    text = msg.text + f'\n\n<b>Сообщение создано и отправлено администратором. Если требуется ответ, напишите администратору @{admin[0].user} напрямую</b>'
    for usr in users: bot.send_message(usr.chat_id, text, parse_mode = 'HTML')

    msg.delete()

    bot.delete_message(admin[0].chat_id, admin[0].msg_id)
    bot.send_message(admin[0].chat_id, f'Сообщение, запланированное на {now[0:2]}.{now[2:4]} {now[5:7]}:{now[7:9]} отправлено всем пользователям бота')
except Message.DoesNotExist:
    print('Для отправки ничего не найдено')