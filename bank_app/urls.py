from django.contrib import admin
from django.urls import path
from . import views

app_name = 'bank_app'


urlpatterns = [
   path('', views.index, name='index'),
   path('home/', views.home, name='home'),
   path('staff/', views.staff, name='staff'),
   ]
