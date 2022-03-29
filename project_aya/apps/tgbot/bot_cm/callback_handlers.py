from main.models import User, Vacancy, Message
from .keyboards import keyboard
from .functions import registration_customer, registration_specialist, search_master

def callbacks(bot, callback_message):
    admin = User.objects.filter(role="Админ")
    user = User.objects.filter(chat_id=callback_message.from_user.id)
    messages = Message.objects.filter(clue = "bot_msgs")

    bot.send_message(callback_message.from_user.id, callback_message)

    if len(admin) == 0: admin_id = 248598993
    else: admin_id = admin[0].chat_id

    if callback_message.data.find('confirm_user') >= 0:
        user_id = callback_message.data[callback_message.data.rfind('_')+1:len(callback_message.data)]
        bot.delete_message(user_id, user[0].msg_id)
        bot.send_message(user_id, "✅ Администрация подтвердила Ваш аккаунт!", reply_markup = keyboard('customer') if user[0].role == 'Заказчик' else keyboard('specialist'))
        bot.send_message(admin_id, 'Аккаунт пользователя '+user[0].user+'(Имя: '+user[0].name+' ID: '+user_id+') подтверждён')
        return
    if callback_message.data.find('reject_user') >= 0:
        user_id = callback_message.data[callback_message.data.rfind('_')+1:len(callback_message.data)]
        bot.delete_message(user_id, user[0].msg_id)
        person = User.objects.get(chat_id=user_id)
        person.delete()
        bot.send_message(user_id, "🚫 Администрация отклонила Ваш аккаунт! Попробуйте зарегистрироваться заново\n\nУкажите кто Вы:", reply_markup = keyboard('start'))
        bot.send_message(admin_id, 'Аккаунт пользователя '+user[0].user+'(Имя: '+user[0].name+' ID: '+user_id+') отклонён')
        return
    if callback_message.data.find('to_bot') >= 0:
        vacancy_id = callback_message.data[callback_message.data.rfind('_')+1:len(callback_message.data)]
        _vacancy = Vacancy.objects.filter(id=vacancy_id)
        users = User.objects.filter(city=_vacancy.city, role="Исполнитель")
        for usr in users:
            name = User.objects.filter(chat_id=_vacancy.chat_id).values("name")
            msg_text = '⭕️ Новый Заказ\n\n'
            msg_text += '▫️ Описание:\n'+_vacancy.role+'\n\n'
            msg_text += '👤 Имя заказчика: '+name[0]+'\n'
            bot.send_message(usr.chat_id, msg_text, reply_markup = keyboard('vacancy_to_bot', {'username': usr.user}))
        user = User.objects.filter(chat_id=_vacancy.chat_id)
        if len(user) > 0: bot.delete_message(_vacancy.chat_id, user[0].msg_id)
        bot.send_message(_vacancy.chat_id, "✅ Администрация подтвердила Ваше объявление с ID "+vacancy_id)
        bot.send_message(admin_id, 'Вы подтвердили и отправили пользователям бота объявление с ID '+vacancy_id)
        return
    if callback_message.data.find('to_channel') >= 0:
        vacancy_id = callback_message.data[callback_message.data.rfind('_')+1:len(callback_message.data)]
        _vacancy = Vacancy.objects.filter(id=vacancy_id)
        user = User.objects.filter(chat_id=_vacancy.chat_id)
        msg_text = '⭕️ Новый Заказ\n\n'
        msg_text += '▫️ Описание:\n'+_vacancy.role+'\n\n'
        msg_text += '👤 Имя заказчика: '+user[0].name+'\n'
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
        #bot.send_message('@digitaljobkz', msg_text, reply_markup = keyboard('vacancy_to_bot', {'username': username[0][0]}))
        bot.send_message(groups.get(_vacancy.city), msg_text, reply_markup = keyboard('vacancy_to_bot', {'username': user[0].user}))
        if len(user) > 0: bot.delete_message(_vacancy.chat_id, user[0].msg_id)
        bot.send_message(_vacancy.chat_id, "✅ Администрация подтвердила Ваше объявление с ID "+vacancy_id)
        bot.send_message(admin_id, 'Вы подтвердили и отправили в канал объявление с ID '+vacancy_id)
        return
    if callback_message.data.find('reject_vacancy') >= 0:
        vacancy_id = callback_message.data[callback_message.data.rfind('_')+1:len(callback_message.data)]
        _vacancy = Vacancy.objects.filter(id=vacancy_id)
        user = User.objects.filter(chat_id=_vacancy.chat_id)
        if len(user) > 0: bot.delete_message(_vacancy.chat_id, user[0].msg_id)
        bot.send_message(_vacancy.chat_id, "🚫 Администрация удалила Ваше объявление с ID "+str(vacancy_id))
        bot.send_message(admin_id, 'Вы отклонили объявление с ID '+vacancy_id)
        vac = Vacancy.objects.get(id=vacancy_id)
        vac.delete()
        return
    if callback_message.data == 'send_now':
        user = User.objects.filter(chat_id=admin_id)
        if len(user) > 0: bot.delete_message(admin_id, user[0].msg_id)
        res = bot.send_message(admin_id, 'Отправьте текст сообщения для отправки')
        user[0].msg_id = res.id
        user[0].mode = "send_now"
        user[0].save()
        return
    if callback_message.data == 'send_on_time':
        user = User.objects.filter(chat_id=admin_id)
        if len(user) > 0: bot.delete_message(admin_id, user[0].msg_id)
        res = bot.send_message(admin_id, 'Отправьте текст сообщения для отправки')
        user[0].msg_id = res.id
        user[0].mode = "send_on_time"
        user[0].step = 1
        user[0].save()
        Message.objects.create(clue="on_time_msg")
        return
    if callback_message.data == 'start_accept':
        bot.delete_message(callback_message.from_user.id, user[0].msg_id)
        res = bot.send_message(callback_message.from_user.id, 'Выберите кто Вы:', reply_markup = keyboard('who_you_are'))
        user[0].msg_id = res.id
        user[0].step = 0
        user[0].save()
        return
    if callback_message.data == 'customer':
        user[0].step = 1
        user[0].save()
        registration_customer(bot, callback_message)
        return
    if callback_message.data == 'specialist':
        user[0].step = 1
        user[0].save()
        registration_specialist(bot, callback_message)
        return
    if callback_message.data.find('city_') >= 0:
        search_params = {}
        if user[0].mode == 'search':
            search_params['city'] = callback_message.data[callback_message.data.find('_')+1:len(callback_message.data)]
            search_master(bot, callback_message, search_params)
        elif user[0].mode == 'edit_city':
            user[0].city = callback_message.data[callback_message.data.index('_')+1:len(callback_message.data)]
            user[0].mode = ""
            user[0].save()
            bot.send_message(callback_message.from_user.id, 'Город изменён.')
        elif user[0].mode == 'one_click_vacancy':
            if len(user) > 0: bot.delete_message(callback_message.from_user.id, user[0].msg_id)
            res = bot.send_message(callback_message.from_user.id, messages[1].text)
            user[0].msg_id = res.id
            user[0].mode = ""
            user[0].save()
            _vacancy = Vacancy.objects.filter(chat_id=callback_message.from_user.id)
            _vacancy.city = callback_message.data[callback_message.data.find('_')+1:len(callback_message.data)]
            _vacancy.save()
            admin_msg_text = 'Пользователь '+user[0].user+' (Имя: '+user[0].name+' ID: '+str(user[0].chat_id)+') создал объявление!'
            admin_msg_text += '\n\nID вакансии: '+str(_vacancy.id)+'\n\nГород, куда опубликовать: '+_vacancy.city+'\nТекст:\n'+_vacancy.role
            bot.send_message(admin_id, admin_msg_text, reply_markup = keyboard('approve_vacancy', {'vacancy': _vacancy.id}))
        else:
            if user[0].role == 'Заказчик':
                user[0].step = 4
                user[0].save()
                registration_customer(bot, callback_message)
            elif user[0].role == 'Исполнитель':
                user[0].step = 4
                user[0].save()
                registration_specialist(bot, callback_message)
        return
    if callback_message.data.find('exp_') >= 0:
        if user[0].mode == 'search':
            search_params['experience'] = callback_message.data[callback_message.data.find('_')+1:len(callback_message.data)]
            search_master(bot, callback_message, search_params)
        elif user[0].mode == 'edit_experience':
            user[0].experience = callback_message.data[callback_message.data.index('_')+1:len(callback_message.data)]
            user[0].mode = ""
            user[0].save()
            bot.send_message(callback_message.from_user.id, 'Опыт работы изменен.')
        else:
            user[0].step = 5
            user[0].save()
            registration_specialist(bot, callback_message)
        return
    if callback_message.data.find('spec_') >= 0:
        if user[0].mode == 'search':
            search_params['speciality'] = callback_message.data[callback_message.data.find('_')+1:len(callback_message.data)]
            search_master(bot, callback_message, search_params)
        elif user[0].mode == 'edit_speciality':
            user[0].speciality = callback_message.data[callback_message.data.index('_')+1:len(callback_message.data)]
            user[0].mode = ""
            user[0].save()
            bot.send_message(callback_message.from_user.id, 'Специализация изменена.')
        else:
            user[0].step = 6
            user[0].save()
            registration_specialist(bot, callback_message)
        return
    if callback_message.data == 'skip_photo':
        user[0].step = 7
        user[0].save()
        registration_specialist(bot, callback_message, 1)
        return
    if callback_message.data == 'skip_portfolio':
        user[0].step = 8
        user[0].save()
        registration_specialist(bot, callback_message, 1)
        return
    if callback_message.data == 'skip_description':
        user[0].step = 9
        user[0].save()
        registration_specialist(bot, callback_message, 1)
        return
    if callback_message.data.find('confirm_text') >= 0:
        if len(user) > 0: bot.delete_message(callback_message.from_user.id, user[0].msg_id)
        res = bot.send_message(callback_message.from_user.id, 'Ваше объявление выйдет в ближайшее время!\nКофе☕️, Чай🍃, Воду? :)')
        user[0].msg_id = res.id
        user[0].save()
        _vacancy = Vacancy.objects.order_by("-id").first()
        admin_msg_text = 'Пользователь '+user[0].user+' (Имя: '+user[0].name+' ID: '+str(user[0].chat_id)+') создал объявление!'
        admin_msg_text += '\n\nID вакансии: '+str(_vacancy.id)+'\nОписание:\n'+_vacancy.role
        bot.send_message(admin_id, admin_msg_text, reply_markup = keyboard('approve_vacancy', {'vacancy': _vacancy.id}))
    if callback_message.data.find('reject_text') >= 0:
        vacancy_id = callback_message.data[callback_message.data.rfind('_')+1:len(callback_message.data)]
        vac = Vacancy.objects.get(id=vacancy_id)
        vac.delete()
        if len(user) > 0: bot.delete_message(callback_message.from_user.id, user[0].msg_id)
        bot.send_message(callback_message.from_user.id, "🚫 Вы удалили объявление. Вы можете подать его повторно.")

    bot.answer_callback_message_query(callback_message.id)
