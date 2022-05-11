from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from .models import Account
from django.contrib.auth.models import User
from .forms import createAccount


def index(request):
   return render(request, 'bank_app/index.html')

def index(request):
   return render(request, 'bank_app/index.html')

@login_required
def home(request):
   user = request.user 
   if request.method == "POST":
      print("Hello")
      account_form = createAccount(request.POST)
      if account_form.is_valid():
         Account.objects.create(user=User.objects.get(pk=user.id), title=account_form.cleaned_data['title'])
   if request.user.is_staff:
      return render(request, 'bank_app/staff.html')
   else:
      context = {
         'form':createAccount,
         'accounts':Account.objects.all(),
         'user_id':user.id,
      }
      return render(request, 'bank_app/home.html', context)


# Admin 

@login_required
def staff(request):
   assert request.user.is_staff, 'Not for regular customers, only for admin'

   return render(request, 'bank_app/staff.html')

