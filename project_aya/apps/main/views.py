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