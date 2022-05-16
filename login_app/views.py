from django.shortcuts import render, reverse
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login as dj_login, logout as dj_logout
from django.http import HttpResponseRedirect
from bank_app.models import Customer
from bank_app.forms import createCustomer


def login(request):
   context = {}

   if request.method == "POST":
      user = authenticate(request, username=request.POST['user'], password=request.POST['password'])
      print("hello user")
      print(user.password)
      if user:
            dj_login(request, user)
            return HttpResponseRedirect(reverse('bank_app:home'))

      else:
            context = {
               'error': 'Wrong username or password.'
            }
   return render(request, 'login_app/login.html', context)


def logout(request):
   dj_logout(request)
   return render(request, 'login_app/login.html')


def password_reset(request):
   pass


def sign_up(request):
   context = {}
   if request.method == "POST":
      customer_form = createCustomer(request.POST)
      password = request.POST['password']
      confirm_password = request.POST['confirm_password']
      username = request.POST['user']
      first_name = request.POST['first_name']
      last_name = request.POST['last_name']
      email = request.POST['email']
      phone_number = request.POST['phone_number']
      customer_rank = "basic"
      user = User.objects.create_user(
            username=username, 
            first_name=first_name, 
            last_name=last_name, 
            email=email, 
            password=password
      )
      Customer.objects.create(user=user, phone_number=phone_number, customer_rank=customer_rank)
      if password == confirm_password:
            if user:
               return HttpResponseRedirect(reverse('login_app:login'))
            else:
               context = {
                  'error': 'Could not create user account - please try again.'
               }
      else:
            context = {
               'error': 'Passwords did not match. Please try again.'
            }
   return render(request, 'login_app/sign_up.html', context)



def delete_account(request):
   pass
