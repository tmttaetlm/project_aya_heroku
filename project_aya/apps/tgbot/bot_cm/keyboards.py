from telebot import types

def keyboard(type, params = {}):
    if type == 'start':
        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(types.InlineKeyboardButton('Согласен', callback_data = 'start_accept'))
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
    if type == 'who_you_are':
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
