import json
import os
from xml.etree.ElementInclude import include
import requests
from django.shortcuts import render
from django.http import JsonResponse
from django.views import View

from .models import User

# Create your views here.
def index(request):
    if User.objects.count() == 0:
        param = {}
    else:
        param = {'specialists': User.objects.filter(role="Исполнитель")}
    return render(request, 'main/list.html', param)

class bot_webhook(View):
    def post(self, request, *args, **kwargs):
        import telebot, sqlite3
        from sqlite3 import Error

        bot = telebot.TeleBot('5299933627:AAFadtni2QPlSxeikWyTYNN-DukFGkm_KY0')

        t_data = json.loads(request.body)
        bot.send_message(248598993, t_data)
        """
        def read_query(query, params = {}):
            connection = sqlite3.connect('..../db.sqlite3')
            cursor = connection.cursor()
            result = None
            try:
                cursor.execute(query, params)
                result = cursor.fetchall()
                return result
            except Error as e:
                print(f"The error '{e}' occurred")

        admin = read_query('select chat_id, user from main_user where role = "Админ"', {})
        if len(admin) == 0:
            admin_id = 248598993
            admin_name = 'Медет'
            #admin_id = 469614681
        else:
            admin_id = admin[0][0]
            admin_name = admin[0][1]

        bot.send_message(248598993, 'Есть контакт')
        """
        #include('.../bot/bot.py')

        return JsonResponse({"ok": "POST request processed"})