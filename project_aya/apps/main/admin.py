from django.contrib import admin

from .models import User, Vacancy, Message

admin.site.register(User)
admin.site.register(Message)
admin.site.register(Vacancy)