from django.shortcuts import render
from django.http import JsonResponse

from .models import User

# Create your views here.
def index(request):
    if User.objects.count() == 0:
        param = {}
    else:
        param = {'specialists': User.objects.filter(role="Исполнитель")}
    return render(request, 'main/list.html', param)

def bot(request):
    if request.method == 'GET':
        data = ' method GET'
    elif request.method == 'POST':
        data = ' method POST'
    else:
        data = ''
    a = {'Hello world': data}
    response = JsonResponse(a)
    response['Access-Control-Allow-Origin'] = '*'
    return response