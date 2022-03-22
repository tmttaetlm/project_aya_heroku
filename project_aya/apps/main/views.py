import json
from .tgbot import aya_bot
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
        aya_bot.main(json.loads(request.body))
        return JsonResponse({"ok": "POST request processed"})