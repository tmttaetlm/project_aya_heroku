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
        t_data = json.loads(request.body)
        t_message = t_data["message"]
        t_chat = t_message["chat"]

        include('.../bot/bot.py')

        return JsonResponse({"ok": "POST request processed"})