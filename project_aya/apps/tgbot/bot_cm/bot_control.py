from datetime import datetime
from main.models import User, Message, Vacancy
from .keyboards import keyboard
from .functions import search_master

def control(bot, message):
    admin = User.objects.filter(role='Админ')
    bot_user = User.objects.get(chat_id=message.from_user.id)
    messages = Message.objects.filter(clue='bot_msgs')
    if len(admin) == 0:
        admin_id = 248598993
        admin_name = 'dos_augustous'
        #admin_id = 469614681
    else:
        admin_id = admin[0].chat_id
        admin_name = admin[0].user

    # Меню администратора
    if message.text == '👤 Пользователи':
        users = User.objects.exclude(role='Админ').order_by('-id')[:10]
        msg = 'Последние 10 зарегистрировавщихся пользователей:\n\n'
        for user in users:
            reg_date = datetime.strptime(user.registration_date, '%d.%m.%Y %H:%M:%S')
            msg += 'Имя: '+user.name+'\nНомер телефона: '+user.phone+'\nГород: '+user.city+'\nДата регистрации: '+reg_date.strftime('%d.%m.%Y %H:%M:%S')+'\nНаписать в телеграм: @'+user.user+'\n\n'
        bot.send_message(admin_id, msg)
    if message.text == '📄 Объявления':
        vacancies = Vacancy.objects.order_by('-id')[:10]
        msg = 'Последние 10 опубликованных объявлений:\n\n'
        for vacancy in vacancies:
            author = User.objects.filter(chat_id = vacancy.chat_id)
            msg += 'Дата публикации: '+vacancy.date.strftime('%d.%m.%Y %H:%M:%S')+'\nТекст: '+vacancy.text+'\nАвтор: '+author.name+'\nНаписать автору: @'+author[0].user+'\n\n'
        bot.send_message(admin_id, msg)
    if message.text == '💬 Опубликовать сообщение':
        res = bot.send_message(admin_id, 'Как вы хотите отправить сообщение боту?', reply_markup = keyboard('send_to_bot'))
        admin.msg_id = res.id
        admin.save()
    # Сторона заказчика
    if message.text == '⚡️ Разместить вакансию в 1 клик':
        bot_user.mode = 'one_click_vacancy'
        bot_user.save()
        bot.send_message(message.from_user.id, messages[1].text.replace('br', '\n'))
        return
    if message.text == '🔎 Поиск специалиста':
        bot_user.mode = 'search'
        bot_user.step = 1
        bot_user.save()
        search_master(bot, message)
        return
    # Общие функции
    if message.text == '📇 Мой аккаунт':
        bot_user.mode = 'edit_account'
        bot_user.save()
        bot.send_message(message.from_user.id, 'Редактирование аккаунта', reply_markup = keyboard('edit_customer_account') if bot_user.role == 'Заказчик' else keyboard('edit_specialist_account'))
    if message.text == '📨 Написать админу':
        bot.send_message(message.from_user.id, 'Аккаунт администратора @'+admin_name+'\nВы можете напрямую написать ему.')
    if message.text == '📰 Купить рекламу в боте':
        bot.send_message(message.from_user.id, 'Для размещения рекламы напишите @'+admin_name)
    if message.text == '🔙 Назад':
        bot_user.mode = ''
        bot_user.save()
        bot.send_message(message.from_user.id, 'Главное меню', reply_markup = keyboard('customer') if bot_user.role == 'Заказчик' else keyboard('specialist'))
    # Редактирование профиля общее
    if message.text == '✅ Изменить имя':
        bot_user.mode = 'edit_name'
        bot_user.save()
        bot.send_message(message.from_user.id, 'Напишите мне ваше имя')
    if message.text == '🏢 Изменить город':
        bot_user.mode = 'edit_city'
        bot_user.save()
        bot.send_message(message.from_user.id, 'Выберите город из списка', reply_markup = keyboard('cities'))
    if message.text == '📱 Изменить номер телефона':
        bot_user.mode = 'edit_phone'
        bot_user.save()
        bot.send_message(message.from_user.id, 'Отправьте новый номер телефона или воспользуйтесь кнопкой ниже', reply_markup = keyboard('phone_request'))
    if message.text == '🚮 Удалить мой аккаунт':
        person = User.objects.get(chat_id=message.from_user.id)
        person.delete()
        bot.send_message(message.from_user.id, 'Рады были с вами поработать. Всего хорошего!\n\nЧтобы зарегистрироваться повторно отправьте боту команду /start')
    # Редактирование профиля заказчика
    if message.text == '😕 Я не Заказчик':
        bot_user.role = None
        bot_user.name = None
        bot_user.phone = None
        bot_user.city = None
        bot_user.mode = 'registration'
        bot_user.step = 1
        bot_user.save()
        res = bot.send_message(message.from_user.id, 'Выберите кто Вы:', reply_markup = keyboard('start'))
        bot_user.msg_id = res.id
        bot_user.save()
    # Редактирование профиля исполнителя
    if message.text == '💪 Изменить специализацию':
        bot_user.mode = 'edit_speciality'
        bot_user.save()
        bot.send_message(message.from_user.id, 'Выберите специализацию', reply_markup = keyboard('speciality'))
    if message.text == '⏰ Изменить опыт работы':
        bot_user.mode = 'edit_experience'
        bot_user.save()
        bot.send_message(message.from_user.id, 'Укажите опыт работы', reply_markup = keyboard('experience'))
    if message.text == '📂 Изменить ссылку портфолио':
        bot_user.mode = 'edit_portfolio'
        bot_user.save()
        bot.send_message(message.from_user.id, 'Отправьте ссылку на портфолио')
    if message.text == '📷 Изменить фото':
        bot_user.mode = 'edit_photo'
        bot_user.save()
        bot.send_message(message.from_user.id, 'Отправьте мне фото')
    if message.text == '✌ Изменить описание о себе':
        bot_user.mode = 'edit_description'
        bot_user.save()
        bot.send_message(message.from_user.id, 'Напишите пару слов о себе')
    if message.text == '😕 Я не Специалист':
        bot_user.role = None
        bot_user.name = None
        bot_user.phone = None
        bot_user.city = None
        bot_user.experience = None
        bot_user.speciality = None
        bot_user.photo_url = None
        bot_user.portfolio_url = None
        bot_user.description = None
        bot_user.mode = 'registration'
        bot_user.step = 1
        bot_user.save()
        res = bot.send_message(message.from_user.id, 'Выберите кто Вы:', reply_markup = keyboard('start'))
        bot_user.msg_id = res.id
        bot_user.save()
