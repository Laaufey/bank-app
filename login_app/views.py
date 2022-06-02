
from multiprocessing import context
from pydoc import cli

from django.shortcuts import redirect, render, reverse
from django.contrib.auth.models import User
import pyqrcode
import os
import environ
from twilio.rest import Client
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

import uuid
from django.contrib.auth import authenticate, login as dj_login, logout as dj_logout
from django.http import HttpResponseRedirect
from bank_app.models import Customer
from bank_app.forms import createCustomer


env = environ.Env()
environ.Env.read_env()





def add_verify(request):
   print("Add_verify view")
   print(request.user)
   # account_sid = env("TWILIO_ACCOUNT_SID")
   # auth_token = env('TWILIO_AUTH_TOKEN')
   # service_sid = env('TWILIO_SERVICE_SID')
   # client = Client(account_sid, auth_token)
   # if request.method == "POST":
   #    print("POSTING")
   #    if 'authenticate' in request.POST:
   #       print("TOTP")
   #       print(request.user.customer.totp_identity)
   #       factor = client.verify.services(service_sid) \
   #                            .entities(request.user.customer.totp_identity) \
   #                            .factors(factor.secret) \
   #                            .update(auth_payload=request.POST['totp_code'])
   #       print(factor.status)
   #       if factor.status == 'verified':
   #          return HttpResponseRedirect(reverse('bank_app:home'))
   #       else:
   #          return render(request, 'login_app/add_verify.html', {'error':'Could not verify, please try again'})
   # if request.method == "POST":

   #    client = Client(account_sid, auth_token)

   #    factors = client.verify.services(service_sid) \
   #                         .entities(request.user.customer.totp_identity) \
   #                         .factors \
   #                         .list(limit=20)

   #    for record in factors:
   #       user_factor = record.sid

   #    factor = client.verify.services(service_sid) \
   #                            .entities(request.user.customer.totp_identity) \
   #                            .factors(user_factor) \
   #                            .update(auth_payload=request.POST['totp_code'])
   #    if factor.status == 'verified':
   #       return HttpResponseRedirect(reverse('login_app:login'))
   #       # return render(request, 'login_app/login.html')
   #    else:
   #       return render(request, 'login_app/add_verify.html', {'error':'Could not verify, please try again'})
   return render(request, 'login_app/add_verify.html')

def verify(request):
   print('Here Now')
   if request.method == "POST":
      print("here hello")
      # account_sid = os.environ.get("TWILIO_ACCOUNT_SID")
      # auth_token = os.environ.get('TWILIO_AUTH_TOKEN')
      # service_sid = os.environ.get('TWILIO_SERVICE_SID')
      
      # client = Client(account_sid, auth_token)

      # factors = client.verify.services(service_sid) \
      #                      .entities(request.user.customer.totp_identity) \
      #                      .factors \
      #                      .list(limit=20)

      # for record in factors:
      #    user_factor = record.sid
      #    print(factors)
      # print(request.user.customer.totp_identity)
      # print("user factor")
      # print(record)
      # print(user_factor)
      # challenge = client.verify \
      #                   .services(service_sid) \
      #                   .entities(request.user.customer.totp_identity) \
      #                   .challenges \
      #                   .create(
      #                      auth_payload=request.POST['totp_code'],
      #                      factor_sid=request.user.customer.totp_identity
      #                   )

      # print(challenge.status)
      # if challenge.status == 'verified':
      return HttpResponseRedirect(reverse('bank_app:home'))
      #    # return render(request, 'bank_app/home.html')
      # else:
      #    return render(request, 'login_app/verify.html', {'error':'Could not verify, please try again'})
   return render(request, 'login_app/verify.html')

def login(request):
   context = {}
   if 'login' in request.POST:
      if request.method == "POST":
         print("HERE LOGIN")
         user = authenticate(request, username=request.POST['user'], password=request.POST['password'])
         print("hello user")
         if user:
               request.session['pk'] = user.pk
               dj_login(request, user)
               return HttpResponseRedirect(reverse('login_app:verify'))
               # return render(request, 'home.html')
         else:
            context = {
                  'error': 'Wrong username or password.'
               }
   return render(request, 'login_app/login.html', context)


def logout(request):
   dj_logout(request)
   # return render(request, 'login_app/login.html')
   return HttpResponseRedirect(reverse('login_app:login'))


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
      if password == confirm_password:
         enitity_id = uuid.uuid4()
         Customer.objects.create(user=user, phone_number=phone_number, customer_rank=customer_rank, totp_identity=enitity_id)
 
         if user:
            env = environ.Env()
            env.read_env()
            account_sid = env("TWILIO_ACCOUNT_SID")
            auth_token = env('TWILIO_AUTH_TOKEN')
            service_sid = env('TWILIO_SERVICE_SID')
            print("here")
            print(account_sid, account_sid, service_sid)
            client = Client(account_sid, auth_token)

            print("Hello enitity_id")
            print(enitity_id)

            new_factor = client.verify \
                              .services(service_sid) \
                              .entities(enitity_id) \
                              .new_factors \
                              .create(
                                    friendly_name=f"{user.first_name}'s account",
                                    factor_type='totp'
                              )
            print(new_factor.binding)
            print(new_factor.sid)
            factor_obj = new_factor.binding

            url = pyqrcode.create(factor_obj['uri'])
            url.svg('static/login_app/authy-url.svg', scale=2)
            # return HttpResponseRedirect(reverse('login_app:login'))
            return render(request, 'login_app/add_verify.html', {'signupuser':user})
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
