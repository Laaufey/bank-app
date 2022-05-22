from multiprocessing import context
from django.shortcuts import redirect, render, reverse
from django.contrib.auth.models import User
from twilio.rest import Client
import pyqrcode
import os
from django.contrib.auth import authenticate, login as dj_login, logout as dj_logout
from django.http import HttpResponseRedirect
from bank_app.models import Customer
from bank_app.forms import createCustomer



def verify(request):
   url = pyqrcode.create('http://uca.edu')
   url.svg('uca-url.svg', scale=8)
   url.eps('uca-url.eps', scale=2)
   print(url.terminal(quiet_zone=1))

   if request.method == "POST":
      # account_sid = os.environ['TWILIO_ACCOUNT_SID']
      account_sid = os.environ['ACb82a519e91ea148938a5f8f69bd1d989']
      auth_token = os.environ['TWILIO_AUTH_TOKEN']
      client = Client(account_sid, auth_token)

      new_factor = client.verify \
                        .services('Sparion') \
                        .entities('TWILIO_SERVICE_SID') \
                        .new_factors \
                        .create(
                              friendly_name="Taylor's Account Name",
                              factor_type='totp'
                        )

      print(new_factor.binding)
   context = {
         'error': 'Not verified',
      }
   return render(request, 'login_app/verify.html', context)

def login(request):
   context = {}

   if request.method == "POST":
      user = authenticate(request, username=request.POST['user'], password=request.POST['password'])
      print("hello user")
      print(user.password)
      if user:
            request.session['pk'] = user.pk
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
