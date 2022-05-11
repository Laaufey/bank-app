from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from .models import Account


def index(request):
   return render(request, 'bank_app/index.html')

def index(request):
   return render(request, 'bank_app/index.html')

@login_required
def home(request):
   if request.user.is_staff:
      return render(request, 'bank_app/staff.html')
   else:
      return render(request, 'bank_app/home.html')

# Admin 

@login_required
def staff(request):
   assert request.user.is_staff, 'Not for regular customers, only for admin'
   
   return render(request, 'bank_app/staff.html')

