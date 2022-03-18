from django.urls import path
from . import views
from django.views.decorators.csrf import csrf_exempt
from main.views import bot_webhook

urlpatterns =[
    path('', views.index, name = 'index'),
    path('bot/', csrf_exempt(bot_webhook.as_view())),
]