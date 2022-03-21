import json
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
        import telebot

        bot = telebot.TeleBot('5299933627:AAFadtni2QPlSxeikWyTYNN-DukFGkm_KY0')

        t_data = json.loads(request.body)
        t_msg = t_data["message"]
        info_msg = "ID: "+str(t_msg["from"]["id"])+"\n"
        info_msg += "Username: "+t_msg["from"]["username"]+"\n"
        info_msg += "First name: "+t_msg["from"]["first_name"]+"\n"
        if "last_name" in t_msg["from"]:
            info_msg += "Last name: "+t_msg["from"]["last_name"]+"\n"
        info_msg += "Text: "+t_msg["text"]
        bot.send_message(248598993, info_msg)

        return JsonResponse({"ok": "POST request processed"})