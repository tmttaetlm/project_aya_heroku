import re
import telebot
import sqlite3
from sqlite3 import Error
from telebot import types
from crontab import CronTab
from datetime import datetime

def write_query(query, params = {}):
    connection = sqlite3.connect('....../db.sqlite3')
    cursor = connection.cursor()
    try:
        cursor.execute(query, params)
        connection.commit()
        #print('Query executed successfully')
    except Error as e:
        print(f"The error '{e}' occurred")

def read_query(query, params = {}):
    connection = sqlite3.connect('....../db.sqlite3')
    cursor = connection.cursor()
    result = None
    try:
        cursor.execute(query, params)
        result = cursor.fetchall()
        return result
    except Error as e:
        print(f"The error '{e}' occurred")

def bot_control(message):
    chat_id = message.from_user.id
    # Меню администратора
    if message.text == '👤 Пользователи':
        users = read_query('select * from main_user where role <> "Админ" order by id desc limit 10')
        msg = 'Последние 10 зарегистрировавщихся пользователей:\n\n'
        for user in users:
            reg_date = datetime.strptime(user[12], "%d.%m.%Y %H:%M:%S")
            msg += 'Имя: '+user[4]+'\nНомер телефона: '+user[5]+'\nГород: '+user[6]+'\nДата регистрации: '+reg_date.strftime("%d.%m.%Y %H:%M:%S")+'\nНаписать в телеграм: @'+user[2]+'\n\n'
        bot.send_message(admin_id, msg)
    if message.text == '📄 Объявления':
        vacancies = read_query('select * from main_vacancy order by id desc limit 10')
        msg = 'Последние 10 опубликованных объявлений:\n\n'
        for vacancy in vacancies:
            user = read_query('select * from main_user where chat_id = :chat_id', {'chat_id': vacancy[1]})
            msg += 'Дата публикации: '+vacancy[4].strftime("%d.%m.%Y %H:%M:%S")+'\nТекст: '+vacancy[3]+'\nАвтор: '+user[4]+'\nНаписать автору: @'+user[2]+'\n\n'
        bot.send_message(admin_id, msg)
    if message.text == '💬 Опубликовать сообщение':
        res = bot.send_message(admin_id, 'Как вы хотите отправить сообщение боту?', reply_markup = keyboards('send_to_bot'))
        write_query('update main_user set msg_id = :msg_id where chat_id = :chat_id', {'chat_id': admin_id, 'msg_id': res.id})
    # Сторона заказчика
    if message.text == '⚡️ Разместить вакансию в 1 клик':
        write_query('update main_user set mode = "one_click_vacancy" where chat_id = :chat_id', {'chat_id': chat_id})
        bot.send_message(chat_id, messages[0][1])
        return
    if message.text == '🔎 Поиск специалиста':
        write_query('update main_user set mode = "search", step = 1 where chat_id = :chat_id', {'chat_id': chat_id})
        search_master(message)
        return
    # Общие функции
    if message.text == '📇 Мой аккаунт':
        user = read_query('select * from main_user where chat_id = :chat_id', {'chat_id': chat_id})
        write_query('update main_user set mode = "edit_account" where chat_id = :chat_id', {'chat_id': chat_id})
        bot.send_message(chat_id, 'Редактирование аккаунта', reply_markup = keyboards('edit_customer_account') if user[0][3] == 'Заказчик' else keyboards('edit_specialist_account'))
    if message.text == '📨 Написать админу':
        bot.send_message(chat_id, 'Аккаунт администратора @'+admin_name+'\nВы можете напрямую написать ему.')
    if message.text == '📰 Купить рекламу в боте':
        bot.send_message(chat_id, 'Для размещения рекламы напишите @'+admin_name)
    if message.text == '🔙 Назад':
        user = read_query('select * from main_user where chat_id = :chat_id', {'chat_id': chat_id})
        write_query('update main_user set mode = "" where chat_id = :chat_id', {'chat_id': chat_id})
        bot.send_message(chat_id, 'Главное меню', reply_markup = keyboards('customer') if user[0][3] == 'Заказчик' else keyboards('specialist'))
    # Редактирование профиля общее
    if message.text == '✅ Изменить имя':
        write_query('update main_user set mode = "edit_name" where chat_id = :chat_id', {'chat_id': chat_id})
        bot.send_message(chat_id, 'Напишите мне ваше имя')
    if message.text == '🏢 Изменить город':
        write_query('update main_user set mode = "edit_city" where chat_id = :chat_id', {'chat_id': chat_id})
        bot.send_message(chat_id, 'Выберите город из списка', reply_markup = keyboards('cities'))
    if message.text == '📱 Изменить номер телефона':
        write_query('update main_user set mode = "edit_phone" where chat_id = :chat_id', {'chat_id': chat_id})
        bot.send_message(chat_id, 'Отправьте новый номер телефона или воспользуйтесь кнопкой ниже', reply_markup = keyboards('phone_request'))
    if message.text == '🚮 Удалить мой аккаунт':
        write_query('delete from main_user where chat_id = :chat_id', {'chat_id': chat_id})
        bot.send_message(chat_id, 'Рады были с вами поработать. Всего хорошего!\n\nЧтобы зарегистрироваться повторно отправьте боту команду /start')
    # Редактирование профиля заказчика
    if message.text == '😕 Я не Заказчик':
        write_query('update main_user set role = NULL, name = NULL, phone = NULL, city = NULL, mode = "registration", step = 1 where chat_id = :chat_id', {'chat_id': message.from_user.id})
        res = bot.send_message(message.from_user.id, 'Выберите кто Вы:', reply_markup = keyboards('start'))
        write_query('update main_user set msg_id = :msg_id where chat_id = :chat_id', {'chat_id': message.from_user.id, 'msg_id': res.id})
    # Редактирование профиля исполнителя
    if message.text == '💪 Изменить специализацию':
        write_query('update main_user set mode = "edit_speciality" where chat_id = :chat_id', {'chat_id': chat_id})
        bot.send_message(chat_id, 'Выберите специализацию', reply_markup = keyboards('speciality'))
    if message.text == '⏰ Изменить опыт работы':
        write_query('update main_user set mode = "edit_experience" where chat_id = :chat_id', {'chat_id': chat_id})
        bot.send_message(chat_id, 'Укажите опыт работы', reply_markup = keyboards('experience'))
    if message.text == '📂 Изменить ссылку портфолио':
        write_query('update main_user set mode = "edit_portfolio" where chat_id = :chat_id', {'chat_id': chat_id})
        bot.send_message(chat_id, 'Отправьте ссылку на портфолио')
    if message.text == '📷 Изменить фото':
        write_query('update main_user set mode = "edit_photo" where chat_id = :chat_id', {'chat_id': chat_id})
        bot.send_message(chat_id, 'Отправьте мне фото')
    if message.text == '✌ Изменить описание о себе':
        write_query('update main_user set mode = "edit_description" where chat_id = :chat_id', {'chat_id': chat_id})
        bot.send_message(chat_id, 'Напишите пару слов о себе')
    if message.text == '😕 Я не Специалист':
        write_query('update main_user set role = NULL, name = NULL, phone = NULL, city = NULL, experience = NULL, speciality = NULL, photo_url = NULL, portfolio_url = NULL, description = NULL, mode = "registration", step = 1 where chat_id = :chat_id', {'chat_id': message.from_user.id})
        res = bot.send_message(message.from_user.id, 'Выберите кто Вы:', reply_markup = keyboards('start'))
        write_query('update main_user set msg_id = :msg_id where chat_id = :chat_id', {'chat_id': message.from_user.id, 'msg_id': res.id})  
    
def create_one_click_vacancy(data):
    chat_id = data.from_user.id
    params = {
        'chat_id': chat_id,
        'msg_id': data.id,
        'text': data.text,
        'date': datetime.now(),
    }
    write_query('insert into main_vacancy (chat_id, msg_id, text, date) values (:chat_id, :msg_id, :text, :date)', params)
    text = 'Ваше объявление:\n\n'
    text += data.text+'\n\n'
    text += 'Выберите в группу какого города хотите опубликовать:'
    res = bot.send_message(data.from_user.id, text, reply_markup = keyboards('cities'))
    write_query('update main_user set msg_id = :msg_id where chat_id = :chat_id', {'chat_id': data.from_user.id, 'msg_id': res.id})

def create_task(dt_val):
    cron = CronTab(user=True)
    #job = cron.new(command='python ~/project_aya/send_to_bot.py')
    job = cron.new(command='python3 ~/Code/python/project_aya/bot/send_to_bot.py', comment = dt_val)
    job.day.on(int(dt_val[0:2]))
    job.month.on(int(dt_val[2:4]))
    job.hour.on(int(dt_val[5:7]))
    job.minute.on(int(dt_val[7:9]))
    cron.write()

def search_master(data):
    user = read_query('select * from main_user where chat_id = :chat_id', {'chat_id': data.from_user.id})
    if user[0][14] == 'search' and user[0][15] == 1:
        write_query('update main_user set step = 2 where chat_id = :chat_id', {'chat_id': data.from_user.id})
        bot.send_message(data.from_user.id, 'Укажите специальность:', reply_markup = keyboards('speciality'))
    if user[0][14] == 'search' and user[0][15] == 2:
        write_query('update main_user set step = 3 where chat_id = :chat_id', {'chat_id': data.from_user.id})
        bot.send_message(data.from_user.id, 'Укажите опыт работы:', reply_markup = keyboards('experience'))
    if user[0][14] == 'search' and user[0][15] == 3:
        write_query('update main_user set step = 4 where chat_id = :chat_id', {'chat_id': data.from_user.id})
        bot.send_message(data.from_user.id, 'Укажите город из списка:', reply_markup = keyboards('cities'))
    if user[0][14] == 'search' and user[0][15] == 4:
        write_query('update main_user set step = 0, mode = "" where chat_id = :chat_id', {'chat_id': data.from_user.id})
        result = read_query('select * from main_user where city = :city and experience = :experience and speciality = :speciality and role = "Исполнитель" limit 10', search_params)
        msg = 'Специалисты, соответствующие вашим критериям поиска:\n\n'
        for row in result:
            msg += 'Имя: '+row[4]+'\nНомер телефона: '+row[5]+'\nСсылка на портфолио: '+row[10]+'\nНаписать в телеграм: @'+row[2]+'\n\n'
        bot.send_message(data.from_user.id, msg)
    return

def registration_customer(data):
    chat_id = data.from_user.id
    user = read_query('select * from main_user where chat_id = :chat_id', {'chat_id': chat_id})
    if user[0][14] != 'registration': return
    if user[0][15] == 1:
        if len(user) > 0: bot.delete_message(chat_id, user[0][13])
        res = bot.send_message(chat_id, '📱 Отправьте Ваш номер телефон (необязательно)', reply_markup = keyboards('phone_request'))
        write_query('update main_user set role = :role, msg_id = :msg_id where chat_id = :chat_id', {'role': 'Заказчик', 'msg_id': res.id, 'chat_id': chat_id})
        return
    if user[0][15] == 2:
        keyboard = types.ReplyKeyboardRemove()
        if len(user) > 0: bot.delete_message(chat_id, user[0][13])
        res = bot.send_message(chat_id, '☺️ Как к Вам обращаться?', reply_markup = keyboard)
        if data.text == 'Пропустить':
            write_query('update main_user set phone = :phone, msg_id = :msg_id where chat_id = :chat_id', {'phone': data.text, 'msg_id': res.id, 'chat_id': chat_id})
        else:
            if data.contact is None:
                write_query('update main_user set msg_id = :msg_id where chat_id = :chat_id', {'msg_id': res.id, 'chat_id': chat_id})
            else:
                write_query('update main_user set phone = :phone, msg_id = :msg_id where chat_id = :chat_id', {'phone': data.contact.phone_number, 'msg_id': res.id, 'chat_id': chat_id})
        return
    if user[0][15] == 3:
        if len(user) > 0: bot.delete_message(chat_id, user[0][13])
        res = bot.send_message(chat_id, '🏙 Ваш город?', reply_markup = keyboards('cities'))
        write_query('update main_user set name = :name, msg_id = :msg_id where chat_id = :chat_id', {'name': data.text, 'msg_id': res.id, 'chat_id': chat_id})
        return
    if user[0][15] == 4:
        if len(user) > 0: bot.delete_message(chat_id, user[0][13])
        res = bot.send_message(chat_id, 'Поздравляю с успешной регистрацией! После подтверждения администратором Вы сможете использовать функционал бота!')
        write_query('update main_user set city = :city, msg_id = :msg_id, mode = "", step = 0 where chat_id = :chat_id', {'city': data.data[data.data.index('_')+1:len(data.data)], 'msg_id': res.id, 'chat_id': chat_id})
        msg = 'Пользователь '+user[0][2]+' завершил регистрацию!\n\nИмя: '+user[0][4]+'\nID: '+str(user[0][1])+'\nType: '+user[0][3]+'\nТелефон: '+str(user[0][5])
        bot.send_message(admin_id, msg, reply_markup = keyboards('approve_user', {"user": user[0][1]}))
        return

def registration_specialist (data, skip = 0):
    chat_id = data.from_user.id
    user = read_query('select * from main_user where chat_id = :chat_id', {'chat_id': chat_id})
    if user[0][14] != 'registration': return
    if user[0][15] == 1:
        if len(user) > 0: bot.delete_message(chat_id, user[0][13])
        res = bot.send_message(chat_id, '📱 Отправьте Ваш номер телефон (необязательно)', reply_markup = keyboards('phone_request'))
        write_query('update main_user set role = :role, msg_id = :msg_id, step = 2 where chat_id = :chat_id', {'role': 'Исполнитель', 'msg_id': res.id, 'chat_id': chat_id})
        return
    if user[0][15] == 2:
        keyboard = types.ReplyKeyboardRemove()
        if len(user) > 0: bot.delete_message(chat_id, user[0][13])
        res = bot.send_message(chat_id, 'Как к Вам обращаться?', reply_markup = keyboard)
        if data.text == 'Пропустить':
            write_query('update main_user set phone = :phone, msg_id = :msg_id, step = 3 where chat_id = :chat_id', {'phone': '-', 'msg_id': res.id, 'chat_id': chat_id})
        else:
            write_query('update main_user set phone = :phone, msg_id = :msg_id, step = 3 where chat_id = :chat_id', {'phone': data.contact.phone_number, 'msg_id': res.id, 'chat_id': chat_id})
        return
    if user[0][15] == 3:
        if len(user) > 0: bot.delete_message(chat_id, user[0][13])
        res = bot.send_message(chat_id, 'Ваш город?', reply_markup = keyboards('cities'))
        write_query('update main_user set name = :name, msg_id = :msg_id, step = 4 where chat_id = :chat_id', {'name': data.text, 'msg_id': res.id, 'chat_id': chat_id})
        return
    if user[0][15] == 4:
        if len(user) > 0: bot.delete_message(chat_id, user[0][13])
        res = bot.send_message(chat_id, 'Укажите опыт работы', reply_markup = keyboards('experience'))
        write_query('update main_user set city = :city, msg_id = :msg_id where chat_id = :chat_id', {'city': data.data[data.data.index('_')+1:len(data.data)], 'msg_id': res.id, 'chat_id': chat_id})
        return
    if user[0][15] == 5:
        if len(user) > 0: bot.delete_message(chat_id, user[0][13])
        res = bot.send_message(chat_id, 'Укажите специальность', reply_markup = keyboards('speciality'))
        write_query('update main_user set experience = :experience, msg_id = :msg_id where chat_id = :chat_id', {'experience': data.data[data.data.index('_')+1:len(data.data)], 'msg_id': res.id, 'chat_id': chat_id})
        return
    if user[0][15] == 6:
        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(types.InlineKeyboardButton('Пропустить', callback_data = 'skip_photo'))
        if len(user) > 0: bot.delete_message(chat_id, user[0][13])
        res = bot.send_message(chat_id, 'Загрузите вашу фотография', reply_markup = keyboard)
        write_query('update main_user set speciality = :speciality, msg_id = :msg_id where chat_id = :chat_id', {'speciality': data.data[data.data.index('_')+1:len(data.data)], 'msg_id': res.id, 'chat_id': chat_id})
        return
    if user[0][15] == 7:
        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(types.InlineKeyboardButton('Пропустить', callback_data = 'skip_portfolio'))
        if len(user) > 0: bot.delete_message(chat_id, user[0][13])
        res = bot.send_message(chat_id, 'Отправьте ссылку на портфолио', reply_markup = keyboard)
        if skip:
            write_query('update main_user set photo_url = :photo_url, msg_id = :msg_id where chat_id = :chat_id', {'photo_url': '-', 'msg_id': res.id, 'chat_id': chat_id})
        else:
            write_query('update main_user set photo_url = :photo_url, msg_id = :msg_id where chat_id = :chat_id', {'photo_url': data.photo[-1].file_id, 'msg_id': res.id, 'chat_id': chat_id})
        return
    if user[0][15] == 8:
        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(types.InlineKeyboardButton('Пропустить', callback_data = 'skip_description'))
        if len(user) > 0: bot.delete_message(chat_id, user[0][13])
        res = bot.send_message(chat_id, 'Раскажите немного о себе', reply_markup = keyboard)
        if skip:
            write_query('update main_user set portfolio_url = :portfolio_url, msg_id = :msg_id where chat_id = :chat_id', {'portfolio_url': '-', 'msg_id': res.id, 'chat_id': chat_id})
        else:
            write_query('update main_user set portfolio_url = :portfolio_url, msg_id = :msg_id where chat_id = :chat_id', {'portfolio_url': data.text, 'msg_id': res.id, 'chat_id': chat_id})
        return
    if user[0][15] == 9:
        if len(user) > 0: bot.delete_message(chat_id, user[0][13])
        res = bot.send_message(chat_id, 'Поздравляю с успешной регистрацией! После подтверждения администратором Вы сможете использовать функционал бота!')
        if skip:
            write_query('update main_user set description = :description, msg_id = :msg_id, step = 0, mode = "" where chat_id = :chat_id', {'description': '-', 'msg_id': res.id, 'chat_id': chat_id})
        else:
            write_query('update main_user set description = :description, msg_id = :msg_id, step = 0, mode = "" where chat_id = :chat_id', {'description': data.text, 'msg_id': res.id, 'chat_id': chat_id})
        msg = 'Пользователь '+user[0][2]+' завершил регистрацию!\n\nИмя: '+user[0][4]+'\nID: '+str(user[0][1])+'\nType: '+user[0][3]+'\nТелефон: '+str(user[0][5])
        bot.send_message(admin_id, msg, reply_markup = keyboards('approve_user', {"user": user[0][1]}))
        return

def keyboards(type, params = {}):
    if type == 'customer':
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard = True)
        keyboard.add(types.KeyboardButton('⚡️ Разместить вакансию в 1 клик'))
        keyboard.add(types.KeyboardButton('🔎 Поиск специалиста')) 
        keyboard.add(types.KeyboardButton('📇 Мой аккаунт'))
        keyboard.add(types.KeyboardButton('📨 Написать админу'))
        keyboard.add(types.KeyboardButton('📰 Купить рекламу в боте'))
    if type == 'specialist':
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard = True)
        keyboard.add(types.KeyboardButton('📇 Мой аккаунт'))
        keyboard.add(types.KeyboardButton('📝 Написать админу'))
        keyboard.add(types.KeyboardButton('📰 Купить рекламу в боте'))
    if type == 'admin':
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard = True)
        keyboard.add(types.KeyboardButton('👤 Пользователи'))
        keyboard.add(types.KeyboardButton('📄 Объявления'))
        keyboard.add(types.KeyboardButton('💬 Опубликовать сообщение'))
    if type == 'send_to_bot':
        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(types.InlineKeyboardButton('🚀 Моментально', callback_data = 'send_now'))
        keyboard.add(types.InlineKeyboardButton('🕐 В запланированное время (разово)', callback_data = 'send_on_time'))
    if type == 'phone_request':
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard = True)
        keyboard.add(types.KeyboardButton(text = 'Отправить телефон', request_contact = True))
        keyboard.add(types.KeyboardButton(text = 'Пропустить'))
    if type == 'cities':
        keyboard = types.InlineKeyboardMarkup()
        keyboard.row(types.InlineKeyboardButton('Неважно', callback_data = 'city_Неважно'),types.InlineKeyboardButton('Almaty', callback_data = 'city_Almaty'),types.InlineKeyboardButton('Nur-Sultan', callback_data = 'city_Nur-Sultan'))
        keyboard.row(types.InlineKeyboardButton('Shymkent', callback_data = 'city_Shymkent'),types.InlineKeyboardButton('Kyzylorda', callback_data = 'city_Kyzylorda'),types.InlineKeyboardButton('Karagandy', callback_data = 'city_Karagandy'))
        keyboard.row(types.InlineKeyboardButton('Taraz', callback_data = 'city_Taraz'),types.InlineKeyboardButton('Aktau', callback_data = 'city_Aktau'),types.InlineKeyboardButton('Atyrau', callback_data = 'city_Atyrau'))
        keyboard.row(types.InlineKeyboardButton('Aktobe', callback_data = 'city_Aktobe'),types.InlineKeyboardButton('Oral', callback_data = 'city_Oral'),types.InlineKeyboardButton('Petropavl', callback_data = 'city_Petropavl'))
        keyboard.row(types.InlineKeyboardButton('Palvodar', callback_data = 'city_Pavlodar'),types.InlineKeyboardButton('Kostanay', callback_data = 'city_Kostanay'),types.InlineKeyboardButton('Oskemen', callback_data = 'city_Oskemen'))
        keyboard.row(types.InlineKeyboardButton('Semey', callback_data = 'city_Semey'),types.InlineKeyboardButton('Taldykorgan', callback_data = 'city_Taldykorgan'),types.InlineKeyboardButton('Zhezkazgan', callback_data = 'city_Zhezkazgan'))
    if type == 'experience':
        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(types.InlineKeyboardButton('Менее года', callback_data = 'exp_less-one'))
        keyboard.add(types.InlineKeyboardButton('1-3 года', callback_data = 'exp_one-three'))
        keyboard.add(types.InlineKeyboardButton('Более 3 лет', callback_data = 'exp_more-three'))
    if type == 'speciality':
        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(types.InlineKeyboardButton('SMM продвижение', callback_data = 'spec_SMM продвижение'),types.InlineKeyboardButton('Дизайн', callback_data = 'spec_Дизайн'))
        keyboard.add(types.InlineKeyboardButton('Модель', callback_data = 'spec_Модель'),types.InlineKeyboardButton('SEO оптимизация', callback_data = 'spec_SEO оптимизация'))
        keyboard.add(types.InlineKeyboardButton('CRM', callback_data = 'spec_CRM'),types.InlineKeyboardButton('Контекстная реклама', callback_data = 'spec_Контекстная реклама'))
        keyboard.add(types.InlineKeyboardButton('Таргетированная реклама', callback_data = 'spec_Таргетированная реклама'),types.InlineKeyboardButton('Копирайтинг/Перевод', callback_data = 'spec_Копирайтинг/Перевод'))
        keyboard.add(types.InlineKeyboardButton('Разработка сайта (конструкторы)', callback_data = 'spec_Разработка сайта (конструкторы)'),types.InlineKeyboardButton('Разработка чат-бота', callback_data = 'spec_Разработка чат-бота'))
        keyboard.add(types.InlineKeyboardButton('Видеосъемка', callback_data = 'spec_Видеосъемка'),types.InlineKeyboardButton('Фотосъемка', callback_data = 'spec_Фотосъемка'))
        keyboard.add(types.InlineKeyboardButton('Продажи', callback_data = 'spec_Продажи'),types.InlineKeyboardButton('Другое', callback_data = 'spec_Другое'))
    if type == 'approve_user':
        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(types.InlineKeyboardButton('✅ Подтвердить', callback_data = 'confirm_user_'+str(params['user'])))
        keyboard.add(types.InlineKeyboardButton('🚫 Отклонить', callback_data = 'reject_user_'+str(params['user'])))
    if type == 'approve_vacancy':
        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(types.InlineKeyboardButton('✅ Подтвердить (+ в канал)', callback_data = 'to_channel_'+str(params['vacancy'])))
        keyboard.add(types.InlineKeyboardButton('✅ Подтвердить (+ внутрь бота)', callback_data = 'to_bot_'+str(params['vacancy'])))
        keyboard.add(types.InlineKeyboardButton('🚫 Отклонить', callback_data = 'reject_vacancy_'+str(params['vacancy'])))
    if type == 'approve_text':
        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(types.InlineKeyboardButton('✅ Подтвердить', callback_data = 'confirm_text_'+str(params['vacancy'])))
        keyboard.add(types.InlineKeyboardButton('🚫 Удалить', callback_data = 'reject_text_'+str(params['vacancy'])))
    if type == 'start':
        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(types.InlineKeyboardButton('🍊 Исполнитель', callback_data = 'specialist'))
        keyboard.add(types.InlineKeyboardButton('🍒 Заказчик', callback_data = 'customer'))
    if type == 'vacancy_to_bot':
        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(types.InlineKeyboardButton('➡️ Написать заказчику', url = 'https://t.me/'+params['username']))
        keyboard.add(types.InlineKeyboardButton('➡️ Разместить свой заказ', url = 'https://t.me/aya_cyberbot'))
    if type == 'edit_customer_account':
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard = True)
        keyboard.add(types.KeyboardButton('✅ Изменить имя'))
        keyboard.add(types.KeyboardButton('🏢 Изменить город'))
        keyboard.add(types.KeyboardButton('📱 Изменить номер телефона'))
        keyboard.add(types.KeyboardButton('🚮 Удалить мой аккаунт'))
        keyboard.add(types.KeyboardButton('😕 Я не Заказчик'))
        keyboard.add(types.KeyboardButton('🔙 Назад'))
    if type == 'edit_specialist_account':
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard = True)
        keyboard.add(types.KeyboardButton('✅ Изменить имя'))
        keyboard.add(types.KeyboardButton('🏢 Изменить город'))
        keyboard.add(types.KeyboardButton('📱 Изменить номер телефона'))
        keyboard.add(types.KeyboardButton('💪 Изменить специализацию'))
        keyboard.add(types.KeyboardButton('⏰ Изменить опыт работы'))
        keyboard.add(types.KeyboardButton('📂 Изменить ссылку портфолио'))
        keyboard.add(types.KeyboardButton('📷 Изменить фото'))
        keyboard.add(types.KeyboardButton('✌ Изменить описание о себе'))
        keyboard.add(types.KeyboardButton('🚮 Удалить мой аккаунт'))
        keyboard.add(types.KeyboardButton('😕 Я не Специалист'))
        keyboard.add(types.KeyboardButton('🔙 Назад'))
    
    return keyboard  

def main(data):
    bot = telebot.TeleBot('5299933627:AAFadtni2QPlSxeikWyTYNN-DukFGkm_KY0')
    search_params = {}

    admin = read_query('select chat_id, user from main_user where role = "Админ"', {})
    if len(admin) == 0:
        admin_id = 248598993
        admin_name = 'Медет'
        #admin_id = 469614681
    else:
        admin_id = admin[0][0]
        admin_name = admin[0][1]

    messages = read_query('select * from main_message where clue = "bot_msgs"')

    @bot.message_handler(commands=['start'])
    def start_message(message):
        user = read_query('select * from main_user where chat_id = :chat_id', {'chat_id': message.from_user.id})
        if len(user) == 0:
            if message.chat.id == admin_id:
                params = {
                    'chat_id': message.from_user.id,
                    'user': message.from_user.username,
                    'role': 'Админ',
                    'name': 'Администратор'}
                write_query('insert into main_user (chat_id, user, role, name) values (:chat_id, :user, :role, :name)', params)
                bot.send_message(message.chat.id, 'Панель администратора', reply_markup = keyboards('admin'))
            else:
                markup = types.InlineKeyboardMarkup()
                markup.add(types.InlineKeyboardButton('Согласен', callback_data = 'start_accept'))
                res = bot.send_message(message.chat.id, messages[0][1], reply_markup = markup)
                params = {
                    'chat_id': message.from_user.id,
                    'msg_id': res.id,
                    'user': message.from_user.username,
                    'registration_date': datetime.now(),
                    'mode': 'registration',
                    'step': -1}
                write_query('insert into main_user (chat_id, msg_id, user, registration_date, mode, step) values (:chat_id, :msg_id, :user, :registration_date, :mode, :step)', params)
        else:
            if user[0][14] == 'registration':
                if user[0][15] == -1:
                    markup = types.InlineKeyboardMarkup()
                    markup.add(types.InlineKeyboardButton('Согласен', callback_data = 'start_accept'))
                    res = bot.send_message(message.chat.id, '📄 Продолжая пользоваться ботом Вы даете согласие на обработку данных.', reply_markup = markup)
                    write_query('update main_user set msg_id = :msg_id where chat_id = :chat_id', {'chat_id': message.from_user.id, 'msg_id': res.id})
                elif user[0][15] == 0:
                    bot.delete_message(message.from_user.id, user[0][13])
                    res = bot.send_message(message.from_user.id, 'Выберите кто Вы:', reply_markup = keyboards('start'))
                    write_query('update main_user set msg_id = :msg_id where chat_id = :chat_id', {'chat_id': message.from_user.id, 'msg_id': res.id})
                else:
                    if user[0][3] == 'Заказчик': registration_customer(message)
                    elif user[0][3] == 'Исполнитель': registration_specialist(message)
            else:
                if user[0][3] == 'Заказчик': markup = keyboards('customer')
                elif user[0][3] == 'Исполнитель': markup = keyboards('specialist')
                else: markup = keyboards('admin')
                bot.send_message(message.chat.id, 'Рады снова Вас видеть, '+user[0][4], reply_markup = markup)

    @bot.callback_query_handler(func=lambda call: call.from_user.id == admin_id)
    def admin_callbacks(callback):
        if callback.data.find('confirm_user') >= 0:
            user_id = callback.data[callback.data.rfind('_')+1:len(callback.data)]
            user = read_query('select * from main_user where chat_id = :chat_id', {'chat_id': user_id})
            if len(user) > 0:  bot.delete_message(user_id, user[0][13])
            bot.send_message(user_id, "✅ Администрация подтвердила Ваш аккаунт!", reply_markup = keyboards('customer') if user[0][3] == 'Заказчик' else keyboards('specialist'))
            bot.send_message(admin_id, 'Аккаунт пользователя '+user[0][2]+'(Имя: '+user[0][4]+' ID: '+user_id+') подтверждён')
        if callback.data.find('reject_user') >= 0:
            user_id = callback.data[callback.data.rfind('_')+1:len(callback.data)]
            user = read_query('select * from main_user where chat_id = :chat_id', {'chat_id': user_id})
            if len(user) > 0:  bot.delete_message(user_id, user[0][13])
            write_query('delete from main_user where chat_id = :chat_id', {'chat_id': user_id})
            bot.send_message(user_id, "🚫 Администрация отклонила Ваш аккаунт! Попробуйте зарегистрироваться заново\n\nУкажите кто Вы:", reply_markup = keyboards('start'))
            bot.send_message(admin_id, 'Аккаунт пользователя '+user[0][2]+'(Имя: '+user[0][4]+' ID: '+user_id+') отклонён')
        if callback.data.find('to_bot') >= 0:
            vacancy_id = callback.data[callback.data.rfind('_')+1:len(callback.data)]
            vacancy = read_query('select * from main_vacancy where id = :id', {'id': vacancy_id})
            users = read_query('select * from main_user where role = "Исполнитель" and city = :city', {'city': vacancy[0][5]})
            for usr in users:
                name = read_query('select user from main_user where chat_id = :chat_id', {'chat_id': vacancy[0][1]})
                msg_text = '⭕️ Новый Заказ\n\n'
                msg_text += '▫️ Описание:\n'+vacancy[0][3]+'\n\n'
                msg_text += '👤 Имя заказчика: '+name[0][0]+'\n'
                bot.send_message(usr[1], msg_text, reply_markup = keyboards('vacancy_to_bot', {'username': usr[2]}))
            user = read_query('select * from main_user where chat_id = :chat_id', {'chat_id': vacancy[0][1]})
            if len(user) > 0: bot.delete_message(vacancy[0][1], user[0][13])
            bot.send_message(vacancy[0][1], "✅ Администрация подтвердила Ваше объявление с ID "+vacancy_id)
            bot.send_message(admin_id, 'Вы подтвердили и отправили пользователям бота объявление с ID '+vacancy_id)
        if callback.data.find('to_channel') >= 0:
            vacancy_id = callback.data[callback.data.rfind('_')+1:len(callback.data)]
            vacancy = read_query('select * from main_vacancy where id = :id', {'id': vacancy_id})
            user = read_query('select * from main_user where chat_id = :chat_id', {'chat_id': vacancy[0][1]})
            msg_text = '⭕️ Новый Заказ\n\n'
            msg_text += '▫️ Описание:\n'+vacancy[0][3]+'\n\n'
            msg_text += '👤 Имя заказчика: '+user[0][4]+'\n'
            groups = {
                'Неважно': '@kazakhstan_jumys',
                'Almaty': '@almaty_jumys',
                'Nur-Sultan': '@astana_jumys',
                'Shymkent': '@shymkent_job',
                'Kyzylorda': '@qyzylorda_job',
                'Karagandy': '@karagandy_job',
                'Taraz': '@taraz_job',
                'Aktau': '@aktau_jumys',
                'Atyrau': '@atyrau_job',
                'Aktobe': '@jobaktobe',
                'Oral': '@oral_job',
                'Petropavl': '@petropavl_job',
                'Pavlodar': '@job_pavlodar',
                'Kostanay': '@kostanay_job',
                'Oskemen': '@oskemen_job',
                'Semey': '@semey_job',
                'Taldykorgan': '@taldykorgan_jumys',
                'Zhezkazgan': '@jezkazgan_jumys'
            }
            #bot.send_message('@digitaljobkz', msg_text, reply_markup = keyboards('vacancy_to_bot', {'username': username[0][0]}))
            bot.send_message(groups.get(vacancy[0][5]), msg_text, reply_markup = keyboards('vacancy_to_bot', {'username': user[0][2]}))
            if len(user) > 0: bot.delete_message(vacancy[0][1], user[0][13])
            bot.send_message(vacancy[0][1], "✅ Администрация подтвердила Ваше объявление с ID "+vacancy_id)
            bot.send_message(admin_id, 'Вы подтвердили и отправили в канал объявление с ID '+vacancy_id)
        if callback.data.find('reject_vacancy') >= 0:
            vacancy_id = callback.data[callback.data.rfind('_')+1:len(callback.data)]
            vacancy = read_query('select * from main_vacancy where id = :id', {'id': vacancy_id})
            user = read_query('select * from main_user where chat_id = :chat_id', {'chat_id': vacancy[0][1]})
            if len(user) > 0: bot.delete_message(vacancy[0][1], user[0][13])
            bot.send_message(vacancy[0][1], "🚫 Администрация удалила Ваше объявление с ID "+str(vacancy_id))
            bot.send_message(admin_id, 'Вы отклонили объявление с ID '+vacancy_id)
            write_query('delete from main_vacancy where id = :id', {'id': vacancy_id})
        if callback.data == 'send_now':
            user = read_query('select * from main_user where chat_id = :chat_id', {'chat_id': admin_id})
            if len(user) > 0: bot.delete_message(admin_id, user[0][13])
            res = bot.send_message(admin_id, 'Отправьте текст сообщения для отправки')
            write_query('update main_user set msg_id = :msg_id, mode = "send_now" where chat_id = :chat_id', {'chat_id': admin_id, 'msg_id': res.id})
        if callback.data == 'send_on_time':
            user = read_query('select * from main_user where chat_id = :chat_id', {'chat_id': admin_id})
            if len(user) > 0: bot.delete_message(admin_id, user[0][13])
            res = bot.send_message(admin_id, 'Отправьте текст сообщения для отправки')
            write_query('update main_user set msg_id = :msg_id, mode = "send_on_time", step = 1 where chat_id = :chat_id', {'chat_id': admin_id, 'msg_id': res.id})
            write_query('insert into main_message (clue) values ("on_time_msg")')

        bot.answer_callback_query(callback.id)

    @bot.callback_query_handler(func=lambda call: True)
    def user_callbacks(callback):
        user = read_query('select * from main_user where chat_id = :chat_id', {'chat_id': callback.from_user.id})
        if callback.data == 'start_accept':
            bot.delete_message(callback.from_user.id, user[0][13])
            res = bot.send_message(callback.from_user.id, 'Выберите кто Вы:', reply_markup = keyboards('start'))
            write_query('update main_user set step = 0, msg_id = :msg_id where chat_id = :chat_id', {'chat_id': callback.from_user.id, 'msg_id': res.id})
            return
        if callback.data == 'customer':
            write_query('update main_user set step = 1 where chat_id = :chat_id', {'chat_id': callback.from_user.id})
            registration_customer(callback)
            return
        if callback.data == 'specialist':
            write_query('update main_user set step = 1 where chat_id = :chat_id', {'chat_id': callback.from_user.id})
            registration_specialist(callback)
            return
        if callback.data.find('city_') >= 0:
            if user[0][14] == 'search':
                search_params['city'] = callback.data[callback.data.find('_')+1:len(callback.data)]
                search_master(callback)
            elif user[0][14] == 'edit_city':
                write_query('update main_user set city = :city, mode = "" where chat_id = :chat_id', {'city': callback.data[callback.data.index('_')+1:len(callback.data)], 'chat_id': callback.from_user.id})
                bot.send_message(callback.from_user.id, 'Город изменён.')
            elif user[0][14] == 'one_click_vacancy':
                if len(user) > 0: bot.delete_message(callback.from_user.id, user[0][13])
                res = bot.send_message(callback.from_user.id, messages[0][2])
                write_query('update main_user set msg_id = :msg_id, mode = "" where chat_id = :chat_id', {'chat_id': callback.from_user.id, 'msg_id': res.id})
                write_query('update main_vacancy set city = :city where chat_id = :chat_id', {'chat_id': callback.from_user.id, 'city': callback.data[callback.data.find('_')+1:len(callback.data)]})
                vacancy = read_query('select * from main_vacancy order by id desc limit 1')
                admin_msg_text = 'Пользователь '+user[0][2]+' (Имя: '+user[0][4]+' ID: '+str(user[0][1])+') создал объявление!'
                admin_msg_text += '\n\nID вакансии: '+str(vacancy[0][0])+'\n\nГород, куда опубликовать: '+vacancy[0][5]+'\nТекст:\n'+vacancy[0][3]
                bot.send_message(admin_id, admin_msg_text, reply_markup = keyboards('approve_vacancy', {'vacancy': vacancy[0][0]}))
            else:
                if user[0][3] == 'Заказчик':
                    write_query('update main_user set step = 4 where chat_id = :chat_id', {'chat_id': callback.from_user.id})
                    registration_customer(callback)
                elif user[0][3] == 'Исполнитель':
                    write_query('update main_user set step = 4 where chat_id = :chat_id', {'chat_id': callback.from_user.id})
                    registration_specialist(callback)
            return
        if callback.data.find('exp_') >= 0:
            if user[0][14] == 'search':
                search_params['experience'] = callback.data[callback.data.find('_')+1:len(callback.data)]
                search_master(callback)
            elif user[0][14] == 'edit_experience':
                write_query('update main_user set experience = :experience, mode = "" where chat_id = :chat_id', {'experience': callback.data[callback.data.index('_')+1:len(callback.data)], 'chat_id': callback.from_user.id})
                bot.send_message(callback.from_user.id, 'Опыт работы изменен.')
            else:
                write_query('update main_user set step = 5 where chat_id = :chat_id', {'chat_id': callback.from_user.id})
                registration_specialist(callback)
            return
        if callback.data.find('spec_') >= 0:
            if user[0][14] == 'search':
                search_params['speciality'] = callback.data[callback.data.find('_')+1:len(callback.data)]
                search_master(callback)
            elif user[0][14] == 'edit_speciality':
                write_query('update main_user set speciality = :speciality, mode = "" where chat_id = :chat_id', {'speciality': callback.data[callback.data.index('_')+1:len(callback.data)], 'chat_id': callback.from_user.id})
                bot.send_message(callback.from_user.id, 'Специализация изменена.')
            else:
                write_query('update main_user set step = 6 where chat_id = :chat_id', {'chat_id': callback.from_user.id})
                registration_specialist(callback)
            return
        if callback.data == 'skip_photo':
            write_query('update main_user set step = 7 where chat_id = :chat_id', {'chat_id': callback.from_user.id})
            registration_specialist(callback, 1)
            return
        if callback.data == 'skip_portfolio':
            write_query('update main_user set step = 8 where chat_id = :chat_id', {'chat_id': callback.from_user.id})
            registration_specialist(callback, 1)
            return
        if callback.data == 'skip_description':
            write_query('update main_user set step = 9 where chat_id = :chat_id', {'chat_id': callback.from_user.id})
            registration_specialist(callback, 1)
            return
        if callback.data.find('confirm_text') >= 0:
            if len(user) > 0: bot.delete_message(callback.from_user.id, user[0][13])
            res = bot.send_message(callback.from_user.id, 'Ваше объявление выйдет в ближайшее время!\nКофе☕️, Чай🍃, Воду? :)')
            write_query('update main_user set msg_id = :msg_id where chat_id = :chat_id', {'chat_id': callback.from_user.id, 'msg_id': res.id})
            vacancy = read_query('select * from main_vacancy order by id desc limit 1')
            admin_msg_text = 'Пользователь '+user[0][2]+' (Имя: '+user[0][4]+' ID: '+str(user[0][1])+') создал объявление!'
            admin_msg_text += '\n\nID вакансии: '+str(vacancy[0][0])+'\nОписание:\n'+vacancy[0][3]
            bot.send_message(admin_id, admin_msg_text, reply_markup = keyboards('approve_vacancy', {'vacancy': vacancy[0][0]}))
        if callback.data.find('reject_text') >= 0:
            vacancy_id = callback.data[callback.data.rfind('_')+1:len(callback.data)]
            write_query('delete from main_vacancy where id = :id', {'id': vacancy_id})
            if len(user) > 0: bot.delete_message(callback.from_user.id, user[0][13])
            bot.send_message(callback.from_user.id, "🚫 Вы удалили объявление. Вы можете подать его повторно.")

        bot.answer_callback_query(callback.id)

    @bot.message_handler(content_types=['text', 'contact', 'photo'])
    def get_text_messages(message):
        user = read_query('select * from main_user where chat_id = :chat_id', {'chat_id': message.from_user.id})
        if message.text == 'Пропустить':
            if user[0][14] == 'edit_phone':
                write_query('update main_user set phone = :phone, mode = "" where chat_id = :chat_id', {'phone': '-', 'chat_id': user[0][1]})
                bot.send_message(message.from_user.id, 'Номер телефона изменён.', reply_markup = keyboards('customer') if user[0][3] == 'Заказчик' else keyboards('specialist'))
            else:
                role = read_query('select role from main_user where chat_id = :chat_id', {'chat_id': message.from_user.id})
                if role[0][0] == 'Заказчик':
                    write_query('update main_user set step = 2 where chat_id = :chat_id', {'chat_id': message.from_user.id})
                    registration_customer(message)
                elif role[0][0] == 'Исполнитель': 
                    write_query('update main_user set step = 2 where chat_id = :chat_id', {'chat_id': message.from_user.id})
                    registration_specialist(message)
            return
        if message.contact:
            if user[0][14] == 'edit_phone':
                write_query('update main_user set phone = :phone, mode = "" where chat_id = :chat_id', {'phone': message.contact.phone_number, 'chat_id': message.from_user.id})
                bot.send_message(message.from_user.id, 'Номер телефона изменён.', reply_markup = keyboards('customer') if user[0][3] == 'Заказчик' else keyboards('specialist'))
            else:
                write_query('update main_user set step = 2 where chat_id = :chat_id', {'chat_id': message.from_user.id})
                registration_customer(message)
            return
        if message.photo:
            if user[0][14] == 'edit_photo':
                write_query('update main_user set photo_url = :photo_url, mode = "" where chat_id = :chat_id', {'photo_url': message.photo[-1].file_id, 'chat_id': message.from_user.id})
                bot.send_message(message.from_user.id, 'Ваше фото обновлено.')
            else:
                write_query('update main_user set step = 7 where chat_id = :chat_id', {'chat_id': message.from_user.id})
                registration_specialist(message)
            return
        if user[0][14] == 'registration' and user[0][15] == 1:
            bot.send_message(message.from_user.id, '❗ Отправьте номер телефона с помощью кнопки в зоне клавиатуры.')
        if user[0][14] == 'registration' and user[0][15] == 2:
            if user[0][3] == 'Заказчик':
                write_query('update main_user set step = 3 where chat_id = :chat_id', {'chat_id': message.from_user.id})
                registration_customer(message)
            elif user[0][3] == 'Исполнитель':
                write_query('update main_user set step = 3 where chat_id = :chat_id', {'chat_id': message.from_user.id})
                registration_specialist(message)
            return
        if user[0][14] == 'registration' and user[0][15] == 7:
            write_query('update main_user set step = 8 where chat_id = :chat_id', {'chat_id': message.from_user.id})
            registration_specialist(message)
            return
        if user[0][14] == 'registration' and user[0][15] == 8:
            write_query('update main_user set step = 9 where chat_id = :chat_id', {'chat_id': message.from_user.id})
            registration_specialist(message)
            return
        if user[0][14] == 'one_click_vacancy':
            create_one_click_vacancy(message)
            return
        if user[0][14] == 'edit_phone':
            result = re.match('^(\+7|7|8)(\d{3})(\d{3})(\d{4})(\d*)', message.text)
            if result:
                write_query('update main_user set phone = :phone, mode = "" where chat_id = :chat_id', {'phone': '7'+message.text[-10:len(message.text)], 'chat_id': message.from_user.id})
                bot.send_message(message.from_user.id, 'Номер телефона изменён.', reply_markup = keyboards('customer') if user[0][3] == 'Заказчик' else keyboards('specialist'))
            else:
                bot.send_message(message.from_user.id, '❗ Введенный вами номер телефона не соответствует какому-либо стандарту.')
        if user[0][14] == 'edit_name':
            write_query('update main_user set name = :name, mode = "" where chat_id = :chat_id', {'name': message.text, 'chat_id': message.from_user.id})
            bot.send_message(message.from_user.id, 'Имя изменёно.')
        if user[0][14] == 'edit_portfolio':
            write_query('update main_user set portfolio_url = :portfolio_url, mode = "" where chat_id = :chat_id', {'portfolio_url': message.text, 'chat_id': message.from_user.id})
            bot.send_message(message.from_user.id, 'Ссылка на портфолио обновлена.')
        if user[0][14] == 'edit_description':
            write_query('update main_user set description = :description, mode = "" where chat_id = :chat_id', {'description': message.text, 'chat_id': message.from_user.id})
            bot.send_message(message.from_user.id, 'Раздел о себе обновлен.')
        if user[0][14] == 'send_now':
            user = read_query('select * from main_user where chat_id = :chat_id', {'chat_id': admin_id})
            if len(user) > 0: bot.delete_message(admin_id, user[0][13])
            users = read_query('select * from main_user where role <> "Админ"')
            msg = message.text + f'\n\n<b>Сообщение создано и отправлено администратором. Если требуется ответ, напишите администратору @{admin_name} напрямую</b>'
            for usr in users: bot.send_message(usr[1], msg, parse_mode = 'HTML')
            bot.send_message(admin_id, 'Сообщение отправлено всем пользователям бота.')
            write_query('update main_user set mode = "" where chat_id = :chat_id', {'chat_id': admin_id})
        if user[0][14] == 'send_on_time' and user[0][15] == 1:
            user = read_query('select * from main_user where chat_id = :chat_id', {'chat_id': admin_id})
            if len(user) > 0: bot.delete_message(admin_id, user[0][13])
            res = bot.send_message(admin_id, 'Отправьте дату и время отправки в формате "DDMM_HHMM"')
            write_query('update main_user set msg_id = :msg_id, step = 2 where chat_id = :chat_id', {'chat_id': admin_id, 'msg_id': res.id})
            write_query('update main_message set text = :text where clue = "on_time_msg"', {'text': message.text})
        if user[0][14] == 'send_on_time' and user[0][15] == 2:
            user = read_query('select * from main_user where chat_id = :chat_id', {'chat_id': admin_id})
            if len(user) > 0: bot.delete_message(admin_id, user[0][13])
            res = bot.send_message(admin_id, 'Сообщение сохранено и будет отправлено в указанное вами время')
            write_query('update main_user set msg_id = :msg_id, mode = "", step = 0 where chat_id = :chat_id', {'chat_id': admin_id, 'msg_id': res.id})
            write_query('update main_message set clue = :clue where clue = "on_time_msg"', {'clue': 'on_time_msg|'+message.text})
            create_task(message.text)

        bot_control(message)

#bot.infinity_polling()