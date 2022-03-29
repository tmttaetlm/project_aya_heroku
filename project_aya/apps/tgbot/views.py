from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse

import telebot
import logging
import json

from datetime import datetime

from main.models import User, Message

from .bot_cm.keyboards import keyboard
from .bot_cm.message_handlers import handler
from .bot_cm.callback_handlers import callback
from .bot_cm.bot_control import control
from .bot_cm.functions import registration_customer, registration_specialist

logger = telebot.logger
telebot.logger.setLevel(logging.DEBUG)

bot = telebot.TeleBot(settings.TELEGRAM_TOKEN, threaded=False)

# Обработчик /start
@bot.message_handler(commands=['start'])
def start_message(message):
    admin = User.objects.filter(role="Админ")
    user = User.objects.filter(chat_id=message.from_user.id)
    messages = Message.objects.filter(clue="bot_msgs")
    if len(admin) == 0: admin_id = 248598993
    else: admin_id = admin[0].chat_id

    if len(user) == 0:
        if message.chat.id == admin_id:
            User.objects.create(chat_id=message.from_user.id, user=message.from_user.username, role='Админ', name='Администратор')
            bot.send_message(message.chat.id, 'Панель администратора', reply_markup = keyboard('admin'))
        else:
            res = bot.send_message(message.chat.id, messages[0].text, reply_markup = keyboard('start'))
            User.objects.create(chat_id=message.from_user.id, msg_id=res.id, user=message.from_user.username, registration_date=datetime.now(), mode='registration', step=-1)
    else:
        if user[0].mode == 'registration':
            if user[0].step == -1:
                res = bot.send_message(message.chat.id, messages[0].text, reply_markup = keyboard('start'))
                user[0].msg_id = res.id
                user[0].save()
            elif user.step == 0:
                bot.delete_message(message.from_user.id, user[0].msg_id)
                res = bot.send_message(message.from_user.id, 'Выберите кто Вы:', reply_markup = keyboard('start'))
                user[0].msg_id = res.id
                user[0].save()
            else:
                if user[0].role == 'Заказчик': registration_customer(message)
                elif user[0].role == 'Исполнитель': registration_specialist(message)
        else:
            if user[0].role == 'Заказчик': markup = keyboard('customer')
            elif user[0].role == 'Исполнитель': markup = keyboard('specialist')
            else: markup = keyboard('admin')
            bot.send_message(message.chat.id, 'Рады снова Вас видеть, '+user[0].name, reply_markup = markup)

@bot.callback_query_handler(func=lambda call: True)
def user_callbacks(call):
    callback(bot, call)

@bot.message_handler(content_types=['text', 'contact', 'photo'])
def get_text_messages(message):
    handler(bot, message)
    control(bot, message)

# Обработчик
@csrf_exempt
def process(request):
    try:
        update = telebot.types.Update.de_json(json.loads(request.body))
        bot.process_new_updates([update])
    except Exception as e:
        logger.exception(e)
    return HttpResponse("")