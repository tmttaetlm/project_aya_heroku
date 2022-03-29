from telebot import types
from crontab import CronTab
from datetime import datetime
from main.models import User, Vacancy
from .keyboards import keyboard

def create_one_click_vacancy(bot, data):
    Vacancy.objects.create(chat_id=data.from_user.id, msg_id=data.id, text=data.text, date=datetime.now())
    text = 'Ваше объявление:\n\n'
    text += data.text+'\n\n'
    text += 'Выберите в группу какого города хотите опубликовать:'
    res = bot.send_message(data.from_user.id, text, reply_markup = keyboard('cities'))
    user = User.objects.filter(chat_id=data.from_user.id)
    user[0].msg_id = res.id
    user[0].save()

def create_task(bot, dt_val):
    cron = CronTab(user=True)
    #job = cron.new(command='python ~/project_aya/send_to_bot.py')
    job = cron.new(command='python3 ~/Code/python/project_aya/bot/send_to_bot.py', comment = dt_val)
    job.day.on(int(dt_val[0:2]))
    job.month.on(int(dt_val[2:4]))
    job.hour.on(int(dt_val[5:7]))
    job.minute.on(int(dt_val[7:9]))
    cron.write()

def search_master(bot, data, search_params):
    user = User.objects.filter(chat_id=data.from_user.id)
    if user[0].mode == 'search' and user[0].step == 1:
        user[0].step = 2
        user[0].save()
        bot.send_message(data.from_user.id, 'Укажите специальность:', reply_markup = keyboard('speciality'))
    if user[0].mode == 'search' and user[0].step == 2:
        user[0].step = 3
        user[0].save()
        bot.send_message(data.from_user.id, 'Укажите опыт работы:', reply_markup = keyboard('experience'))
    if user[0].mode == 'search' and user[0].step == 3:
        user[0].step = 4
        user[0].save()
        bot.send_message(data.from_user.id, 'Укажите город из списка:', reply_markup = keyboard('cities'))
    if user[0].mode == 'search' and user[0].step == 4:
        user[0].step = 0
        user[0].mode = ''
        user[0].save()
        result = User.objects.filter(city=search_params['city'], experience=search_params['experience'], speciality=search_params['speciality'], role='Исполнитель').order_by('-id')[:10]
        msg = 'Специалисты, соответствующие вашим критериям поиска:\n\n'
        for row in result:
            msg += 'Имя: '+row.name+'\nНомер телефона: '+row.phone+'\nСсылка на портфолио: '+row.portfolio_url+'\nНаписать в телеграм: @'+row.user+'\n\n'
        bot.send_message(data.from_user.id, msg)
    return

def registration_customer(bot, data):
    admin = User.objects.filter(role="Админ")
    user = User.objects.filter(chat_id=data.from_user.id)
    if len(admin) == 0: admin_id = 248598993
    else: admin_id = admin[0].chat_id
    chat_id = data.from_user.id

    if user[0].mode != 'registration': return
    if user[0].step == 1:
        if len(user) > 0: bot.delete_message(chat_id, user[0].msg_id)
        res = bot.send_message(chat_id, '📱 Отправьте Ваш номер телефон (необязательно)', reply_markup = keyboard('phone_request'))
        user[0].role = 'Заказчик'
        user[0].msg_id = res.id
        user[0].save()
        return
    if user[0].step == 2:
        remove_keyboard = types.ReplyKeyboardRemove()
        if len(user) > 0: bot.delete_message(chat_id, user[0].msg_id)
        res = bot.send_message(chat_id, '☺️ Как к Вам обращаться?', reply_markup = remove_keyboard)
        if data.text == 'Пропустить':
            user[0].phone = '-'
            user[0].msg_id = res.id
            user[0].save()
        else:
            if data.contact is None:
                user[0].msg_id = res.id
                user[0].save()
            else:
                user[0].phone = data.contact.phone_number
                user[0].msg_id = res.id
                user[0].save()
        return
    if user[0].step == 3:
        if len(user) > 0: bot.delete_message(chat_id, user[0].msg_id)
        res = bot.send_message(chat_id, '🏙 Ваш город?', reply_markup = keyboard('cities'))
        user[0].name = data.text
        user[0].msg_id = res.id
        user[0].save()
        return
    if user[0].step == 4:
        if len(user) > 0: bot.delete_message(chat_id, user[0].msg_id)
        res = bot.send_message(chat_id, 'Поздравляю с успешной регистрацией! После подтверждения администратором Вы сможете использовать функционал бота!')
        user[0].city = data.data[data.data.index('_')+1:len(data.data)]
        user[0].msg_id = res.id
        user[0].step = 0
        user[0].mode = ''
        user[0].save()
        msg = 'Пользователь @'+user[0].user+' завершил регистрацию!\n\nИмя: '+user[0].name+'\nID: '+str(user[0].chat_id)+'\nType: '+user[0].role+'\nТелефон: +'+str(user[0].phone)
        bot.send_message(admin_id, msg, reply_markup = keyboard('approve_user', {'user': user[0].user}))
        return

def registration_specialist (bot, data, skip = 0):
    admin = User.objects.filter(role="Админ")
    user = User.objects.filter(chat_id=data.from_user.id)
    if len(admin) == 0: admin_id = 248598993
    else: admin_id = admin[0].chat_id
    chat_id = data.from_user.id

    if user[0].mode != 'registration': return
    if user[0].step == 1:
        if len(user) > 0: bot.delete_message(chat_id, user[0].msg_id)
        res = bot.send_message(chat_id, '📱 Отправьте Ваш номер телефон (необязательно)', reply_markup = keyboard('phone_request'))
        user[0].role = 'Исполнитель'
        user[0].msg_id = res.id
        user[0].save()
        return
    if user[0].step == 2:
        remove_keyboard = types.ReplyKeyboardRemove()
        if len(user) > 0: bot.delete_message(chat_id, user[0].msg_id)
        res = bot.send_message(chat_id, 'Как к Вам обращаться?', reply_markup = remove_keyboard)
        if data.text == 'Пропустить':
            user[0].phone = '-'
            user[0].msg_id = res.id
            user[0].save()
        else:
            if data.contact is None:
                user[0].msg_id = res.id
                user[0].save()
            else:
                user[0].phone = data.contact.phone_number
                user[0].msg_id = res.id
                user[0].save()
        return
    if user[0].step == 3:
        if len(user) > 0: bot.delete_message(chat_id, user[0].msg_id)
        res = bot.send_message(chat_id, 'Ваш город?', reply_markup = keyboard('cities'))
        user[0].name = data.text
        user[0].msg_id = res.id
        user[0].save()
        return
    if user[0].step == 4:
        if len(user) > 0: bot.delete_message(chat_id, user[0].msg_id)
        res = bot.send_message(chat_id, 'Укажите опыт работы', reply_markup = keyboard('experience'))
        user[0].city = data.data[data.data.index('_')+1:len(data.data)]
        user[0].msg_id = res.id
        user[0].save()
        return
    if user[0].step == 5:
        if len(user) > 0: bot.delete_message(chat_id, user[0].msg_id)
        res = bot.send_message(chat_id, 'Укажите специальность', reply_markup = keyboard('speciality'))
        user[0].experience = data.data[data.data.index('_')+1:len(data.data)]
        user[0].msg_id = res.id
        user[0].save()
        return
    if user[0].step == 6:
        t_keyboard = types.InlineKeyboardMarkup()
        t_keyboard.add(types.InlineKeyboardButton('Пропустить', callback_data = 'skip_photo'))
        if len(user) > 0: bot.delete_message(chat_id, user[0].msg_id)
        res = bot.send_message(chat_id, 'Загрузите вашу фотография', reply_markup = t_keyboard)
        user[0].speciality = data.data[data.data.index('_')+1:len(data.data)]
        user[0].msg_id = res.id
        user[0].save()
        return
    if user[0].step == 7:
        t_keyboard = types.InlineKeyboardMarkup()
        t_keyboard.add(types.InlineKeyboardButton('Пропустить', callback_data = 'skip_portfolio'))
        if len(user) > 0: bot.delete_message(chat_id, user[0].msg_id)
        res = bot.send_message(chat_id, 'Отправьте ссылку на портфолио', reply_markup = t_keyboard)
        if skip:
            user[0].photo_url = '-'
            user[0].msg_id = res.id
            user[0].save()
        else:
            user[0].photo_url = data.photo[-1].file_id
            user[0].msg_id = res.id
            user[0].save()
        return
    if user[0].step == 8:
        t_keyboard = types.InlineKeyboardMarkup()
        t_keyboard.add(types.InlineKeyboardButton('Пропустить', callback_data = 'skip_description'))
        if len(user) > 0: bot.delete_message(chat_id, user[0].msg_id)
        res = bot.send_message(chat_id, 'Раскажите немного о себе', reply_markup = t_keyboard)
        if skip:
            user[0].portfolio_url = '-'
            user[0].msg_id = res.id
            user[0].save()
        else:
            user[0].portfolio_url = data.text
            user[0].msg_id = res.id
            user[0].save()
        return
    if user[0].step == 9:
        if len(user) > 0: bot.delete_message(chat_id, user[0].msg_id)
        res = bot.send_message(chat_id, 'Поздравляю с успешной регистрацией! После подтверждения администратором Вы сможете использовать функционал бота!')
        if skip:
            user[0].description = '-'
            user[0].msg_id = res.id
            user[0].save()
        else:
            user[0].description = data.text
            user[0].msg_id = res.id
            user[0].save()
        msg = 'Пользователь @'+user[0].user+' завершил регистрацию!\n\nИмя: '+user[0].name+'\nID: '+str(user[0].chat_id)+'\nType: '+user[0].role+'\nТелефон: +'+str(user[0].phone)
        bot.send_message(admin_id, msg, reply_markup = keyboard('approve_user', {'user': user[0].chat_id}))
        return
