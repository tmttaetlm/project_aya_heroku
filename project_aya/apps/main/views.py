from django.shortcuts import render

from .models import User

# Create your views here.
def index(request):
    if User.objects.count() == 0:
        param = {}
    else:
        param = {'specialists': User.objects.all()}
    return render(request, 'main/list.html', param)