import re
from main.models import User, Message
from .keyboards import keyboard
from .functions import registration_customer, registration_specialist, create_one_click_vacancy, create_task

def handler(bot, message):
    admin = User.objects.filter(role='Админ')
    user = User.objects.filter(chat_id=message.from_user.id)

    if len(admin) == 0:
        admin_id = 248598993
        admin_name = 'Медет'
        #admin_id = 469614681
    else:
        admin_id = admin.chat_id
        admin_name = admin[0].name

    if message.text == 'Пропустить':
        if user[0].mode == 'edit_phone':
            user[0].phone = '-'
            user[0].mode = ''
            user[0].save()
            bot.send_message(message.from_user.id, 'Номер телефона изменён.', reply_markup = keyboard('customer') if user[0].role == 'Заказчик' else keyboard('specialist'))
        else:
            user[0].step = 2
            user[0].save()
            if user[0].role == 'Заказчик':
                registration_customer(bot, message)
            elif user[0].role == 'Исполнитель':
                registration_specialist(bot, message)
        return
    if message.contact:
        if user[0].mode == 'edit_phone':
            user[0].phone = message.contact.phone_number
            user[0].mode = ''
            user[0].save()
            bot.send_message(message.from_user.id, 'Номер телефона изменён.', reply_markup = keyboard('customer') if user[0].role == 'Заказчик' else keyboard('specialist'))
        else:
            user[0].step = 2
            user[0].save()
            registration_customer(bot, message)
        return
    if message.photo:
        if user[0].mode == 'edit_photo':
            user[0].photo_url = message.photo[-1].file_id
            user[0].mode = ''
            user[0].save()
            bot.send_message(message.from_user.id, 'Ваше фото обновлено.')
        else:
            user[0].step = 7
            user[0].save()
            registration_specialist(bot, message)
        return
    if user[0].mode == 'registration' and user[0].step == 1:
        bot.send_message(message.from_user.id, '❗ Отправьте номер телефона с помощью кнопки в зоне клавиатуры.')
    if user[0].mode == 'registration' and user[0].step == 2:
        user[0].step = 3
        user[0].save()
        if user[0].role == 'Заказчик':
            registration_customer(bot, message)
        elif user[0].role == 'Исполнитель':
            registration_specialist(bot, message)
        return
    if user[0].mode == 'registration' and user[0].step == 7:
        user[0].step = 8
        user[0].save()
        registration_specialist(bot, message)
        return
    if user[0].mode == 'registration' and user[0].step == 8:
        user[0].step = 9
        user[0].save()
        registration_specialist(bot, message)
        return
    if user[0].mode == 'one_click_vacancy':
        create_one_click_vacancy(bot, message)
        return
    if user[0].mode == 'edit_phone':
        result = re.match('^(\+7|7|8)(\d{3})(\d{3})(\d{4})(\d*)', message.text)
        if result:
            user[0].phone = '7'+message.text[-10:len(message.text)]
            user[0].mode = ''
            user[0].save()
            bot.send_message(message.from_user.id, 'Номер телефона изменён.', reply_markup = keyboard('customer') if user[0].role == 'Заказчик' else keyboard('specialist'))
        else:
            bot.send_message(message.from_user.id, '❗ Введенный вами номер телефона не соответствует какому-либо стандарту.')
    if user[0].mode == 'edit_name':
        user[0].name = message.text
        user[0].mode = ''
        user[0].save()
        bot.send_message(message.from_user.id, 'Имя изменёно.')
    if user[0].mode == 'edit_portfolio':
        user[0].portfolio_url = message.text
        user[0].mode = ''
        user[0].save()
        bot.send_message(message.from_user.id, 'Ссылка на портфолио обновлена.')
    if user[0].mode == 'edit_description':
        user[0].description = message.text
        user[0].mode = ''
        user[0].save()
        bot.send_message(message.from_user.id, 'Раздел о себе обновлен.')
    if user[0].mode == 'send_now':
        bot.delete_message(admin_id, admin.msg_id)
        users = User.objects.exclude(role='Админ')
        msg = message.text + f'\n\n<b>Сообщение создано и отправлено администратором. Если требуется ответ, напишите администратору @{admin_name} напрямую</b>'
        for usr in users: bot.send_message(usr.chat_id, msg, parse_mode = 'HTML')
        bot.send_message(admin_id, 'Сообщение отправлено всем пользователям бота.')
        user[0].mode = ''
        user[0].save()
    if user[0].mode == 'send_on_time' and user[0].step == 1:
        bot.delete_message(admin_id, user[0].msg_id)
        res = bot.send_message(admin_id, 'Отправьте дату и время отправки в формате "DDMM_HHMM"')
        user[0].msg_id = res.id
        user[0].save()
        on_time_msg = Message.objects.filter(clue='on_time_msg')
        on_time_msg.text = message.text
        on_time_msg.save()
    if user[0].mode == 'send_on_time' and user[0].step == 2:
        bot.delete_message(admin_id, admin.msg_id)
        res = bot.send_message(admin_id, 'Сообщение сохранено и будет отправлено в указанное вами время')
        user[0].msg_id = res.id
        user[0].save()
        on_time_msg = Message.objects.filter(clue='on_time_msg')
        on_time_msg.clue = 'on_time_msg|'+message.text
        on_time_msg.save()
        create_task(bot, message.text)