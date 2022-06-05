
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

def sign_up(request):
   context = {}
   env = environ.Env()
   env.read_env()
   account_sid = env("TWILIO_ACCOUNT_SID")
   auth_token = env('TWILIO_AUTH_TOKEN')
   service_sid = env('TWILIO_SERVICE_SID')
   client = Client(account_sid, auth_token)

   if request.method == "POST":
      if "signup" in request.POST:
         customer_form = createCustomer(request.POST)
         password = request.POST['password']
         confirm_password = request.POST['confirm_password']
         username = request.POST['user']
         first_name = request.POST['first_name']
         last_name = request.POST['last_name']
         email = request.POST['email']
         phone_number = request.POST['phone_number']
      
         if password == confirm_password:
            enitity_id = uuid.uuid4()
            user = User.objects.create_user(
               username=username, 
               first_name=first_name, 
               last_name=last_name, 
               email=email, 
               password=password
         )
            Customer.objects.create(user=user, phone_number=phone_number, totp_identity=enitity_id)

            if user:
               new_factor = (
                        client.verify.services(service_sid)
                        .entities(enitity_id)
                        .new_factors.create(
                           friendly_name=f"{user.first_name}'s account", factor_type="totp"
                        )
                     )
               print(new_factor.binding)
               factor_obj = new_factor.binding

               url = pyqrcode.create(factor_obj['uri'])
               url.svg('static/login_app/authy-url.svg', scale=2)
               # return HttpResponseRedirect(reverse('login_app:login'))
               return HttpResponseRedirect(
                  reverse("login_app:add_verify", kwargs={"pk": user.pk})
               )
            else:
               context = {'error': 'Could not create user account - please try again.'}
         else:
               context = {'error': 'Passwords did not match. Please try again.'}
   return render(request, 'login_app/sign_up.html', context)

def add_verify(request, pk):
   context = {}
   user = User.objects.get(pk=pk)
   env = environ.Env()
   env.read_env()
   account_sid = env("TWILIO_ACCOUNT_SID")
   auth_token = env('TWILIO_AUTH_TOKEN')
   service_sid = env('TWILIO_SERVICE_SID')
   client = Client(account_sid, auth_token)

   if request.method == "POST":
      print("POSTING")
      if 'add_verify' in request.POST:
         print("ADD VERIFY IS IN POST")
         register_topt_code = request.POST["add_totp_code"]
         print(register_topt_code)
         factors = (
               client.verify.services(service_sid)
               .entities(user.customer.totp_identity)
               .factors.list(limit=20)
         )

         for record in factors:
               user_factor = record.sid

         factor = (
               client.verify.services(service_sid)
               .entities(user.customer.totp_identity)
               .factors(user_factor)
               .update(auth_payload=register_topt_code)
         )

         if factor.status == "verified":
            print("VERIFIED!!!!!")            
            return HttpResponseRedirect(reverse("login_app:login"))
         else:
               context = {"error": "Wrong code, please try again"}
   else:
      print("NOT POST")
         # pk = user.pk
         # print("add_verify is in the request")
         # factor = client.verify.services(service_sid) \
         #                      .entities(request.user.customer.totp_identity) \
         #                      .factors(factor.secret) \
         #                      .update(auth_payload=request.POST['totp_code'])
         # print("Factor status")
         # print(factor.status)
         # if factor.status == 'verified':
         #    return HttpResponseRedirect(reverse('bank_app:home'))
         # else:
            # return render(request, 'login_app/add_verify.html', {'error':'Could not verify, please try again'})
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
   return render(request, 'login_app/add_verify.html', context)

def login(request):
   context = {}
   if request.method == "POST":
      if 'login' in request.POST:
         user = authenticate(request, username=request.POST['user'], password=request.POST['password'])
         if user:
               request.session['pk'] = user.pk
               dj_login(request, user)
               return HttpResponseRedirect(reverse('login_app:verify'))
               # return render(request, 'home.html')
         else:
            context = {'error': 'Wrong username or password.'}
   return render(request, 'login_app/login.html', context)

def verify(request):
   context = {}
   print('Here Now')
   print("here hello")
   env = environ.Env()
   environ.Env.read_env()
   account_sid = env("TWILIO_ACCOUNT_SID")
   auth_token = env('TWILIO_AUTH_TOKEN')
   service_sid = env('TWILIO_SERVICE_SID')
   client = Client(account_sid, auth_token)
   
   factors = (
      client.verify.services(service_sid)
      .entities(request.user.customer.totp_identity)
      .factors.list(limit=20)
   )

   for record in factors:
      user_factor = record.sid

   if request.method == "POST":
      if "verify" in request.POST:
         print("verify in Post request")
         totp_code = request.POST["totp_code"]

         challenge = (
               client.verify.services(service_sid)
               .entities(request.user.customer.totp_identity)
               .challenges.create(auth_payload=totp_code, factor_sid=user_factor)
         )

         print("Challenge Status: ", challenge.status)

         if challenge.status == "approved":
            print("Challenge Approved")
            return HttpResponseRedirect(reverse('bank_app:home'))
         else:
            print("Challenge Not Approved")
            context = {"error": "Wrong code, please try again"}

   return render(request, 'login_app/verify.html', context)

def logout(request):
   dj_logout(request)
   # return render(request, 'login_app/login.html')
   return HttpResponseRedirect(reverse('login_app:login'))

def password_reset(request):
   pass

def delete_account(request):
   pass
