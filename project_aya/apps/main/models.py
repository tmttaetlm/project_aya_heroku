from atexit import register
from django.db import models

# Create your models here.
class User(models.Model):
    chat_id = models.IntegerField('ID телеграмма')
    user = models.CharField('Пользователь', max_length = 500, null = True)
    role = models.CharField('Роль', max_length = 12, null = True)
    name = models.CharField('Имя', max_length = 100, null = True)
    phone = models.CharField('Номер телефона', max_length = 12, null = True)
    city = models.CharField('Город', max_length = 50, null = True)
    experience = models.CharField('Опыт работы', max_length = 12, null = True)
    speciality = models.CharField('Специализация', max_length = 50, null = True)
    photo_url = models.CharField('Фото', max_length = 500, null = True)
    portfolio_url = models.CharField('Портфолио', max_length = 500, null = True)
    description = models.CharField('О себе', max_length = 1000, null = True)
    registration_date = models.DateTimeField('Дата регистрации', null = True)
    msg_id = models.CharField('ID сообщения', max_length = 1000, null = True)
    mode = models.CharField('Процесс', max_length = 50, null = True)
    step = models.IntegerField('Шаг', null = True)

    def __str__(self):
        return self.user

    class Meta:
        verbose_name = 'Пользователя'
        verbose_name_plural = 'Пользователи'

class Vacancy(models.Model):
    chat_id = models.IntegerField('ID телеграмма')
    msg_id = models.IntegerField('ID сообщения')
    text = models.CharField('Текст', max_length = 500, null = True)
    date = models.DateTimeField('Дата публикации', null = True)
    city = models.CharField('Город для публикации', max_length = 500, null = True)

    def __str__(self):
        return self.text

    class Meta:
        verbose_name = 'Вакансию'
        verbose_name_plural = 'Вакансии'

class Message(models.Model):
    text = models.CharField('Текст', max_length = 1000, null = True)
    clue = models.CharField('Ключ', max_length = 50, null = True)

    def __str__(self):
        return self.text

    class Meta:
        verbose_name = 'Сообщение'
        verbose_name_plural = 'Сообщения'

class Info(models.Model):
    text = models.CharField('Текст', max_length = 1000, null = True)
    clue = models.CharField('Ключ', max_length = 50, null = True)

    def __str__(self):
        return self.clue

    class Meta:
        verbose_name = 'Допольнительное свойство'
        verbose_name_plural = 'Допольнительные свойства'