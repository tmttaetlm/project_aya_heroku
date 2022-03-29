from django.contrib import admin

from .models import User, Vacancy, Message, Info

admin.site.register(User)
admin.site.register(Message)
admin.site.register(Vacancy)
admin.site.register(Info)