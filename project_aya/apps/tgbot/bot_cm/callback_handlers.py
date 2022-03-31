from main.models import User, Vacancy, Message, Info
from .keyboards import keyboard
from .functions import registration_customer, registration_specialist, search_master

def callback(bot, callback_message):
    admin = User.objects.filter(role='Админ')
    bot_user = User.objects.get(chat_id=callback_message.from_user.id)
    messages = Message.objects.filter(clue = 'bot_msgs')

    if len(admin) == 0: admin_id = 248598993
    else: admin_id = admin[0].chat_id

    # User callbacks
    if callback_message.data == 'start_accept':
        bot.delete_message(callback_message.from_user.id, bot_user.msg_id)
        res = bot.send_message(callback_message.from_user.id, 'Выберите кто Вы:', reply_markup = keyboard('who_you_are'))
        bot_user.msg_id = res.id
        bot_user.step = 0
        bot_user.save()
        return
    if callback_message.data == 'customer':
        bot_user.step = 1
        bot_user.save()
        registration_customer(bot, callback_message)
        return
    if callback_message.data == 'specialist':
        bot_user.step = 1
        bot_user.save()
        registration_specialist(bot, callback_message)
        return
    if callback_message.data.find('city_') >= 0:
        if bot_user.mode == 'search':
            Info.objects.create(clue='sp_city', text=callback_message.data[callback_message.data.find('_')+1:len(callback_message.data)])
            search_master(bot, callback_message)
        elif bot_user.mode == 'edit_city':
            bot_user.city = callback_message.data[callback_message.data.index('_')+1:len(callback_message.data)]
            bot_user.mode = None
            bot_user.save()
            bot.send_message(callback_message.from_user.id, 'Город изменён.')
        elif bot_user.mode.rfind('one_click_vacancy_') >= 0:
            _vacancy = Vacancy.objects.get(id=bot_user.mode[bot_user.mode.rfind('_')+1:len(bot_user.mode)])
            _vacancy.city = callback_message.data[callback_message.data.find('_')+1:len(callback_message.data)]
            _vacancy.save()
            bot.delete_message(callback_message.from_user.id, bot_user.msg_id)
            res = bot.send_message(callback_message.from_user.id, messages[2].text.replace('br', '\n'))
            bot_user.msg_id = res.id
            bot_user.step = None
            bot_user.mode = None
            bot_user.save()
            admin_msg_text = 'Пользователь @'+bot_user.user+' (Имя: '+bot_user.name+' ID: '+str(bot_user.chat_id)+') создал объявление!'
            admin_msg_text += '\n\nID вакансии: '+str(_vacancy.id)+'\n\nГород, куда опубликовать: '+_vacancy.city+'\nТекст:\n'+_vacancy.text
            res = bot.send_message(admin_id, admin_msg_text, reply_markup = keyboard('approve_vacancy', {'vacancy': _vacancy.id}))
            admin[0].msg_id = res.id
            admin[0].save()
        else:
            if bot_user.role == 'Заказчик':
                bot_user.step = 4
                bot_user.save()
                registration_customer(bot, callback_message)
            elif bot_user.role == 'Исполнитель':
                bot_user.step = 4
                bot_user.save()
                registration_specialist(bot, callback_message)
        return
    if callback_message.data.find('exp_') >= 0:
        if bot_user.mode == 'search':
            Info.objects.create(clue='sp_exp', text=callback_message.data[callback_message.data.find('_')+1:len(callback_message.data)])
            search_master(bot, callback_message)
        elif bot_user.mode == 'edit_experience':
            bot_user.experience = callback_message.data[callback_message.data.index('_')+1:len(callback_message.data)]
            bot_user.mode = None
            bot_user.save()
            bot.send_message(callback_message.from_user.id, 'Опыт работы изменен.')
        else:
            bot_user.step = 5
            bot_user.save()
            registration_specialist(bot, callback_message)
        return
    if callback_message.data.find('spec_') >= 0:
        if bot_user.mode == 'search':
            Info.objects.create(clue='sp_spec', text=callback_message.data[callback_message.data.find('_')+1:len(callback_message.data)])
            search_master(bot, callback_message)
        elif bot_user.mode == 'edit_speciality':
            bot_user.speciality = callback_message.data[callback_message.data.index('_')+1:len(callback_message.data)]
            bot_user.mode = None
            bot_user.save()
            bot.send_message(callback_message.from_user.id, 'Специализация изменена.')
        else:
            bot_user.step = 6
            bot_user.save()
            registration_specialist(bot, callback_message)
        return
    if callback_message.data == 'skip_photo':
        bot_user.step = 7
        bot_user.save()
        registration_specialist(bot, callback_message, 1)
        return
    if callback_message.data == 'skip_portfolio':
        bot_user.step = 8
        bot_user.save()
        registration_specialist(bot, callback_message, 1)
        return
    if callback_message.data == 'skip_description':
        bot_user.step = 9
        bot_user.save()
        registration_specialist(bot, callback_message, 1)
        return
    if callback_message.data.find('confirm_text') >= 0:
        bot.delete_message(callback_message.from_user.id, bot_user.msg_id)
        res = bot.send_message(callback_message.from_user.id, 'Ваше объявление выйдет в ближайшее время!\nКофе☕️, Чай🍃, Воду? :)')
        bot_user.msg_id = res.id
        bot_user.save()
        _vacancy = Vacancy.objects.order_by('-id').first()
        admin_msg_text = 'Пользователь '+bot_user.user+' (Имя: '+bot_user.name+' ID: '+str(bot_user.chat_id)+') создал объявление!'
        admin_msg_text += '\n\nID вакансии: '+str(_vacancy.id)+'\nОписание:\n'+_vacancy.text
        bot.send_message(admin_id, admin_msg_text, reply_markup = keyboard('approve_vacancy', {'vacancy': _vacancy.id}))
    if callback_message.data.find('reject_text') >= 0:
        vacancy_id = callback_message.data[callback_message.data.rfind('_')+1:len(callback_message.data)]
        vac = Vacancy.objects.get(id=vacancy_id)
        vac.delete()
        bot.delete_message(callback_message.from_user.id, bot_user.msg_id)
        bot.send_message(callback_message.from_user.id, '🚫 Вы удалили объявление. Вы можете подать его повторно.')
    #######################
    # Admin callbacks
    if callback_message.data.find('confirm_user') >= 0:
        user_id = callback_message.data[callback_message.data.rfind('_')+1:len(callback_message.data)]
        tmp_user = User.objects.get(chat_id=user_id)
        bot.delete_message(user_id, tmp_user.msg_id)
        bot.delete_message(admin_id, admin[0].msg_id)
        bot.send_message(user_id, '✅ Администрация подтвердила Ваш аккаунт!', reply_markup = keyboard('customer') if tmp_user.role == 'Заказчик' else keyboard('specialist'))
        bot.send_message(admin_id, 'Аккаунт пользователя '+tmp_user.user+'(Имя: '+tmp_user.name+' ID: '+user_id+') подтверждён')
        return
    if callback_message.data.find('reject_user') >= 0:
        user_id = callback_message.data[callback_message.data.rfind('_')+1:len(callback_message.data)]
        tmp_user = User.objects.get(chat_id=user_id)
        bot.delete_message(user_id, tmp_user.msg_id)
        person = User.objects.get(chat_id=user_id)
        person.delete()
        bot.delete_message(admin_id, admin[0].msg_id)
        bot.send_message(user_id, '🚫 Администрация отклонила Ваш аккаунт! Попробуйте зарегистрироваться заново.')
        bot.send_message(admin_id, 'Аккаунт пользователя '+tmp_user.user+'(Имя: '+tmp_user.name+' ID: '+user_id+') отклонён')
        return
    if callback_message.data.find('to_bot') >= 0:
        vacancy_id = callback_message.data[callback_message.data.rfind('_')+1:len(callback_message.data)]
        _vacancy = Vacancy.objects.get(id=vacancy_id)
        users = User.objects.filter(city=_vacancy.city, role='Исполнитель')
        for usr in users:
            name = User.objects.filter(chat_id=_vacancy.chat_id).values('name')
            msg_text = '⭕️ Новый Заказ\n\n'
            msg_text += '▫️ Описание:\n'+_vacancy.role+'\n\n'
            msg_text += '👤 Имя заказчика: '+name[0]+'\n'
            bot.send_message(usr.chat_id, msg_text, reply_markup = keyboard('vacancy_to_bot', {'username': usr.user}))
        bot_user = User.objects.get(chat_id=_vacancy.chat_id)
        bot.delete_message(_vacancy.chat_id, bot_user.msg_id)
        bot.send_message(_vacancy.chat_id, '✅ Администрация подтвердила Ваше объявление с ID '+vacancy_id)
        bot.delete_message(admin_id, admin[0].msg_id)
        bot.send_message(admin_id, 'Вы подтвердили и отправили пользователям бота объявление с ID '+vacancy_id)
        return
    if callback_message.data.find('to_channel') >= 0:
        vacancy_id = callback_message.data[callback_message.data.rfind('_')+1:len(callback_message.data)]
        _vacancy = Vacancy.objects.get(id=vacancy_id)
        bot_user = User.objects.get(chat_id=_vacancy.chat_id)
        msg_text = '⭕️ Новый Заказ\n\n'
        msg_text += '▫️ Описание:\n'+_vacancy.text+'\n\n'
        msg_text += '👤 Имя заказчика: '+bot_user.name+'\n'
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
        bot.send_message('@tmttae', msg_text, reply_markup = keyboard('vacancy_to_bot', {'username': bot_user.user}))
        #bot.send_message(groups.get(_vacancy.city), msg_text, reply_markup = keyboard('vacancy_to_bot', {'username': bot_user.user}))
        bot.delete_message(_vacancy.chat_id, bot_user.msg_id)
        bot.send_message(_vacancy.chat_id, '✅ Администрация подтвердила Ваше объявление с ID '+vacancy_id)
        bot.delete_message(admin_id, admin[0].msg_id)
        bot.send_message(admin_id, 'Вы подтвердили и отправили в канал объявление с ID '+vacancy_id)
        return
    if callback_message.data.find('reject_vacancy') >= 0:
        vacancy_id = callback_message.data[callback_message.data.rfind('_')+1:len(callback_message.data)]
        _vacancy = Vacancy.objects.get(id=vacancy_id)
        bot_user = User.objects.get(chat_id=_vacancy.chat_id)
        bot.delete_message(_vacancy.chat_id, bot_user.msg_id)
        bot.send_message(_vacancy.chat_id, '🚫 Администрация удалила Ваше объявление с ID '+str(vacancy_id))
        bot.send_message(admin_id, 'Вы отклонили объявление с ID '+vacancy_id)
        vac = Vacancy.objects.get(id=vacancy_id)
        vac.delete()
        return
    if callback_message.data == 'send_now':
        bot.delete_message(admin_id, admin[0].msg_id)
        res = bot.send_message(admin_id, 'Отправьте текст сообщения для отправки')
        admin[0].msg_id = res.id
        admin[0].mode = 'send_now'
        admin[0].save()
        return
    if callback_message.data == 'send_on_time':
        bot.delete_message(admin_id, admin[0].msg_id)
        res = bot.send_message(admin_id, 'Отправьте текст сообщения для отправки')
        admin[0].msg_id = res.id
        admin[0].mode = 'send_on_time'
        admin[0].step = 1
        admin[0].save()
        Message.objects.create(clue='on_time_msg')
        return
    ################
    #bot.answer_callback_message_query(callback_message.id)
