from telebot import types
from crontab import CronTab
from datetime import datetime
from main.models import User, Vacancy, Info
from .keyboards import keyboard

def create_one_click_vacancy(bot, data):
    v = Vacancy.objects.create(chat_id=data.from_user.id, msg_id=data.id, text=data.text, date=datetime.now())
    text = 'Ваше объявление:\n\n'
    text += data.text+'\n\n'
    text += 'Выберите в группу какого города хотите опубликовать:'
    res = bot.send_message(data.from_user.id, text, reply_markup = keyboard('cities'))
    bot_user = User.objects.get(chat_id=data.from_user.id)
    bot_user.msg_id = res.id
    bot_user.mode = bot_user.mode + '_' + str(v.id)
    bot_user.save()

def create_task(bot, dt_val):
    cron = CronTab(user=True)
    #job = cron.new(command='python ~/project_aya/send_to_bot.py')
    job = cron.new(command='python3 ~/Code/python/project_aya/bot/send_to_bot.py', comment = dt_val)
    job.day.on(int(dt_val[0:2]))
    job.month.on(int(dt_val[2:4]))
    job.hour.on(int(dt_val[5:7]))
    job.minute.on(int(dt_val[7:9]))
    cron.write()

def search_master(bot, data):
    bot_user = User.objects.get(chat_id=data.from_user.id)
    if bot_user.mode == 'search' and bot_user.step == 1:
        bot_user.step = 2
        bot_user.save()
        bot.send_message(data.from_user.id, 'Укажите специальность:', reply_markup = keyboard('speciality'))
        return
    if bot_user.mode == 'search' and bot_user.step == 2:
        bot_user.step = 3
        bot_user.save()
        bot.send_message(data.from_user.id, 'Укажите опыт работы:', reply_markup = keyboard('experience'))
        return
    if bot_user.mode == 'search' and bot_user.step == 3:
        bot_user.step = 4
        bot_user.save()
        bot.send_message(data.from_user.id, 'Укажите город из списка:', reply_markup = keyboard('cities'))
        return
    if bot_user.mode == 'search' and bot_user.step == 4:
        bot_user.step = 0
        bot_user.mode = ''
        bot_user.save()
        sp_city = Info.objects.get(clue='sp_city')
        sp_exp = Info.objects.get(clue='sp_exp')
        sp_spec = Info.objects.get(clue='sp_spec')
        result = User.objects.filter(city=sp_city, experience=sp_exp, speciality=sp_spec, role='Исполнитель').order_by('-id')[:10]
        msg = 'Специалисты, соответствующие вашим критериям поиска:\n\n'
        for row in result:
            msg += 'Имя: '+row.name+'\nНомер телефона: '+row.phone+'\nСсылка на портфолио: '+row.portfolio_url+'\nНаписать в телеграм: @'+row.user+'\n\n'
        bot.send_message(data.from_user.id, msg)
        return
    return

def registration_customer(bot, data):
    admin = User.objects.filter(role="Админ")
    bot_user = User.objects.get(chat_id=data.from_user.id)
    if len(admin) == 0: admin_id = 248598993
    else: admin_id = admin[0].chat_id
    chat_id = data.from_user.id

    if bot_user.mode != 'registration': return
    if bot_user.step == 1:
        bot.delete_message(chat_id, bot_user.msg_id)
        res = bot.send_message(chat_id, '📱 Отправьте Ваш номер телефон (необязательно)', reply_markup = keyboard('phone_request'))
        bot_user.role = 'Заказчик'
        bot_user.msg_id = res.id
        bot_user.save()
        return
    if bot_user.step == 2:
        bot.delete_message(chat_id, bot_user.msg_id)
        res = bot.send_message(chat_id, '☺️ Как к Вам обращаться?', reply_markup = keyboard('remove_keyboard'))
        if data.text == 'Пропустить':
            bot_user.phone = '-'
            bot_user.msg_id = res.id
            bot_user.save()
        else:
            if data.contact is None:
                bot_user.msg_id = res.id
                bot_user.save()
            else:
                bot_user.phone = data.contact.phone_number
                bot_user.msg_id = res.id
                bot_user.save()
        return
    if bot_user.step == 3:
        bot.delete_message(chat_id, bot_user.msg_id)
        res = bot.send_message(chat_id, '🏙 Ваш город?', reply_markup = keyboard('cities'))
        bot_user.name = data.text
        bot_user.msg_id = res.id
        bot_user.save()
        return
    if bot_user.step == 4:
        bot.delete_message(chat_id, bot_user.msg_id)
        res = bot.send_message(chat_id, 'Поздравляю с успешной регистрацией! После подтверждения администратором Вы сможете использовать функционал бота!')
        bot_user.city = data.data[data.data.index('_')+1:len(data.data)]
        bot_user.msg_id = res.id
        bot_user.step = 0
        bot_user.mode = ''
        bot_user.save()
        phone = '+'+str(bot_user.phone) if str(bot_user.phone) != '-' else '-'
        msg = 'Пользователь @'+bot_user.user+' завершил регистрацию!\n\nИмя: '+bot_user.name+'\nID: '+str(bot_user.chat_id)+'\nType: '+bot_user.role+'\nТелефон: '+phone
        res = bot.send_message(admin_id, msg, reply_markup = keyboard('approve_user', {'user': bot_user.chat_id}))
        admin[0].msg_id = res.id
        admin[0].save()
        return

def registration_specialist (bot, data, skip = 0):
    admin = User.objects.filter(role="Админ")
    bot_user = User.objects.get(chat_id=data.from_user.id)
    if len(admin) == 0: admin_id = 248598993
    else: admin_id = admin[0].chat_id
    chat_id = data.from_user.id

    if bot_user.mode != 'registration': return
    if bot_user.step == 1:
        bot.delete_message(chat_id, bot_user.msg_id)
        res = bot.send_message(chat_id, '📱 Отправьте Ваш номер телефон (необязательно)', reply_markup = keyboard('phone_request'))
        bot_user.role = 'Исполнитель'
        bot_user.msg_id = res.id
        bot_user.save()
        return
    if bot_user.step == 2:
        bot.delete_message(chat_id, bot_user.msg_id)
        res = bot.send_message(chat_id, 'Как к Вам обращаться?', reply_markup = keyboard('remove_keyboard'))
        if data.text == 'Пропустить':
            bot_user.phone = '-'
            bot_user.msg_id = res.id
            bot_user.save()
        else:
            if data.contact is None:
                bot_user.msg_id = res.id
                bot_user.save()
            else:
                bot_user.phone = data.contact.phone_number
                bot_user.msg_id = res.id
                bot_user.save()
        return
    if bot_user.step == 3:
        bot.delete_message(chat_id, bot_user.msg_id)
        res = bot.send_message(chat_id, 'Ваш город?', reply_markup = keyboard('cities'))
        bot_user.name = data.text
        bot_user.msg_id = res.id
        bot_user.save()
        return
    if bot_user.step == 4:
        bot.delete_message(chat_id, bot_user.msg_id)
        res = bot.send_message(chat_id, 'Укажите опыт работы', reply_markup = keyboard('experience'))
        bot_user.city = data.data[data.data.index('_')+1:len(data.data)]
        bot_user.msg_id = res.id
        bot_user.save()
        return
    if bot_user.step == 5:
        bot.delete_message(chat_id, bot_user.msg_id)
        res = bot.send_message(chat_id, 'Укажите специальность', reply_markup = keyboard('speciality'))
        bot_user.experience = data.data[data.data.index('_')+1:len(data.data)]
        bot_user.msg_id = res.id
        bot_user.save()
        return
    if bot_user.step == 6:
        t_keyboard = types.InlineKeyboardMarkup()
        t_keyboard.add(types.InlineKeyboardButton('Пропустить', callback_data = 'skip_photo'))
        bot.delete_message(chat_id, bot_user.msg_id)
        res = bot.send_message(chat_id, 'Загрузите вашу фотография', reply_markup = t_keyboard)
        bot_user.speciality = data.data[data.data.index('_')+1:len(data.data)]
        bot_user.msg_id = res.id
        bot_user.save()
        return
    if bot_user.step == 7:
        t_keyboard = types.InlineKeyboardMarkup()
        t_keyboard.add(types.InlineKeyboardButton('Пропустить', callback_data = 'skip_portfolio'))
        bot.delete_message(chat_id, bot_user.msg_id)
        res = bot.send_message(chat_id, 'Отправьте ссылку на портфолио', reply_markup = t_keyboard)
        if skip:
            bot_user.photo_url = '-'
            bot_user.msg_id = res.id
            bot_user.save()
        else:
            bot_user.photo_url = data.photo[-1].file_id
            bot_user.msg_id = res.id
            bot_user.save()
        return
    if bot_user.step == 8:
        t_keyboard = types.InlineKeyboardMarkup()
        t_keyboard.add(types.InlineKeyboardButton('Пропустить', callback_data = 'skip_description'))
        bot.delete_message(chat_id, bot_user.msg_id)
        res = bot.send_message(chat_id, 'Раскажите немного о себе', reply_markup = t_keyboard)
        if skip:
            bot_user.portfolio_url = '-'
            bot_user.msg_id = res.id
            bot_user.save()
        else:
            bot_user.portfolio_url = data.text
            bot_user.msg_id = res.id
            bot_user.save()
        return
    if bot_user.step == 9:
        bot.delete_message(chat_id, bot_user.msg_id)
        res = bot.send_message(chat_id, 'Поздравляю с успешной регистрацией! После подтверждения администратором Вы сможете использовать функционал бота!')
        if skip:
            bot_user.description = '-'
            bot_user.msg_id = res.id
            bot_user.save()
        else:
            bot_user.description = data.text
            bot_user.msg_id = res.id
            bot_user.save()
        phone = '+'+str(bot_user.phone) if str(bot_user.phone) != '-' else '-'
        msg = 'Пользователь @'+bot_user.user+' завершил регистрацию!\n\nИмя: '+bot_user.name+'\nID: '+str(bot_user.chat_id)+'\nType: '+bot_user.role+'\nТелефон: '+phone
        res = bot.send_message(admin_id, msg, reply_markup = keyboard('approve_user', {'user': bot_user.chat_id}))
        admin[0].msg_id = res.id
        admin[0].save()
        return
