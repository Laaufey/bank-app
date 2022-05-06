from django.contrib import admin
from django.urls import path

app_name = 'bank_app'

from . import views

urlpatterns = [
   path('', views.index, name='index'),
]
