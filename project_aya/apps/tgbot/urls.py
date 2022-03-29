from django.conf.urls import url
from .views import process

urlpatterns =[
    url('', process),
]