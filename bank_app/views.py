from django.shortcuts import render
from .models import Account


def index(request):
   return render(request, 'bank_app/index.html')
