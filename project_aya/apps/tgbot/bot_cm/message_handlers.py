import re
from main.models import User, Message
from .keyboards import keyboard
from .functions import registration_customer, registration_specialist, create_one_click_vacancy

def handler(bot, message):
    admin = User.objects.filter(role='Админ')
    bot_user = User.objects.get(chat_id=message.from_user.id)

    if len(admin) == 0: admin_id = 248598993
    else: admin_id = admin[0].chat_id

    if message.text == 'Пропустить':
        if bot_user.mode == 'edit_phone':
            bot_user.phone = '-'
            bot_user.mode = None
            bot_user.save()
            bot.send_message(message.from_user.id, 'Номер телефона изменён.', reply_markup = keyboard('customer') if bot_user.role == 'Заказчик' else keyboard('specialist'))
        else:
            bot_user.step = 2
            bot_user.save()
            if bot_user.role == 'Заказчик':
                registration_customer(bot, message)
            elif bot_user.role == 'Исполнитель':
                registration_specialist(bot, message)
        return
    if message.contact:
        if bot_user.mode == 'edit_phone':
            bot_user.phone = message.contact.phone_number
            bot_user.mode = None
            bot_user.save()
            bot.send_message(message.from_user.id, 'Номер телефона изменён.', reply_markup = keyboard('customer') if bot_user.role == 'Заказчик' else keyboard('specialist'))
        else:
            bot_user.step = 2
            bot_user.save()
            registration_customer(bot, message)
        return
    if message.photo:
        if bot_user.mode == 'edit_photo':
            bot_user.photo_url = message.photo[-1].file_id
            bot_user.mode = None
            bot_user.save()
            bot.send_message(message.from_user.id, 'Ваше фото обновлено.', reply_markup = keyboard('customer') if bot_user.role == 'Заказчик' else keyboard('specialist'))
        else:
            bot_user.step = 7
            bot_user.save()
            registration_specialist(bot, message)
        return
    if bot_user.mode == 'registration' and bot_user.step == 1:
        bot.send_message(message.from_user.id, '❗ Отправьте номер телефона с помощью кнопки в зоне клавиатуры.')
    if bot_user.mode == 'registration' and bot_user.step == 2:
        bot_user.step = 3
        bot_user.save()
        if bot_user.role == 'Заказчик':
            registration_customer(bot, message)
        elif bot_user.role == 'Исполнитель':
            registration_specialist(bot, message)
        return
    if bot_user.mode == 'registration' and bot_user.step == 7:
        bot_user.step = 8
        bot_user.save()
        registration_specialist(bot, message)
        return
    if bot_user.mode == 'registration' and bot_user.step == 8:
        bot_user.step = 9
        bot_user.save()
        registration_specialist(bot, message)
        return
    if bot_user.mode == 'one_click_vacancy':
        create_one_click_vacancy(bot, message)
        return
    if bot_user.mode == 'edit_phone':
        result = re.match('^(\+7|7|8)(\d{3})(\d{3})(\d{4})(\d*)', message.text)
        if result:
            bot_user.phone = '7'+message.text[-10:len(message.text)]
            bot_user.mode = None
            bot_user.save()
            bot.send_message(message.from_user.id, 'Номер телефона изменён.', reply_markup = keyboard('customer') if bot_user.role == 'Заказчик' else keyboard('specialist'))
        else:
            bot.send_message(message.from_user.id, '❗ Введенный вами номер телефона не соответствует какому-либо стандарту.')
    if bot_user.mode == 'edit_name':
        bot_user.name = message.text
        bot_user.mode = None
        bot_user.save()
        bot.send_message(message.from_user.id, 'Имя изменёно.', reply_markup = keyboard('customer') if bot_user.role == 'Заказчик' else keyboard('specialist'))
    if bot_user.mode == 'edit_portfolio':
        bot_user.portfolio_url = message.text
        bot_user.mode = None
        bot_user.save()
        bot.send_message(message.from_user.id, 'Ссылка на портфолио обновлена.', reply_markup = keyboard('customer') if bot_user.role == 'Заказчик' else keyboard('specialist'))
    if bot_user.mode == 'edit_description':
        bot_user.description = message.text
        bot_user.mode = None
        bot_user.save()
        bot.send_message(message.from_user.id, 'Раздел о себе обновлен.', reply_markup = keyboard('customer') if bot_user.role == 'Заказчик' else keyboard('specialist'))
    if bot_user.mode == 'send_now':
        bot.delete_message(admin_id, bot_user.msg_id)
        users = User.objects.exclude(role='Админ')
        msg = message.text + f'\n\n<b>Сообщение создано и отправлено администратором. Если требуется ответ, напишите администратору @{admin[0].user} напрямую</b>'
        for usr in users: bot.send_message(usr.chat_id, msg, parse_mode = 'HTML')
        bot.send_message(admin_id, 'Сообщение отправлено всем пользователям бота.')
        bot_user.mode = None
        bot_user.save()
    if bot_user.mode == 'send_on_time' and bot_user.step == 1:
        bot.delete_message(admin_id, bot_user.msg_id)
        res = bot.send_message(admin_id, 'Отправьте дату и время отправки в формате "DDMM_HHMM"')
        bot_user.msg_id = res.id
        bot_user.step = 2
        bot_user.save()
        on_time_msg = Message.objects.filter(clue='on_time_msg').order_by('-id').first()
        on_time_msg.text = message.text
        on_time_msg.save()
        return
    if bot_user.mode == 'send_on_time' and bot_user.step == 2:
        bot.delete_message(admin_id, bot_user.msg_id)
        res = bot.send_message(admin_id, 'Сообщение сохранено и будет отправлено в указанное вами время')
        bot_user.msg_id = res.id
        bot_user.step = None
        bot_user.mode = None
        bot_user.save()
        on_time_msg = Message.objects.filter(clue='on_time_msg').order_by('-id').first()
        on_time_msg.clue = 'on_time_msg|'+message.text
        on_time_msg.save()