from curses.ascii import FF
from multiprocessing import context
from tokenize import blank_re
from django.shortcuts import get_object_or_404, render
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect
from django.views import View
import requests
from .models import Account, Customer, Ledger, ExternalLedger, Bank
from django.contrib.auth.models import User
from .forms import createAccount, createCustomer, createUser, UpdateUserForm, UpdateCustomerForm, TransferForm, LoanForm
from decimal import Decimal
from rest_framework import permissions
from rest_framework import viewsets
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from twilio.rest import Client

def index(request):
   return render(request, 'bank_app/index.html')


@login_required
def home(request):
   user = request.user
   if request.method == "POST":
      account_form = createAccount(request.POST)
      if account_form.is_valid():
         Account.objects.create(user=User.objects.get(pk=user.id), title=account_form.cleaned_data['title'])
   if request.user.is_staff:
      context = {
         'form':createAccount,
         'accounts':Account.objects.all(),
         'user_id':user.id,
         'customers':Customer.objects.all(),
      }
      return render(request, 'bank_app/staff.html', context)
   else:
      context = {
         'form':createAccount,
         'accounts':Account.objects.all(),
         'user_id':user.id,
         'customers':Customer.objects.all(),
      }
      return render(request, 'bank_app/home.html', context)

@login_required
def accounts(request):
   user=request.user
   context = {
      'accounts':Account.objects.all(),
      'user_id':user.id,
      'ledger':Ledger.objects.all(),
      'count':Account.objects.count()
      }
   return render(request, 'bank_app/accounts.html', context)

@login_required
def loans(request):
   user=request.user
   if not request.user.customer.customer_rank == "GOLD" and not request.user.customer.customer_rank == "silver":
      context = {

      }
      return render(request, 'bank_app/loans.html', context)
   if request.method == "POST":
      loan_form = LoanForm(request.POST)
      loan_form.fields['account'].queryset = request.user.customer.accounts
      if loan_form.is_valid():
         amount = loan_form.cleaned_data['amount']
         loan_account = Account.objects.create(user=request.user, title="Loan Account", account_type='Loan Account')
         account = Account.objects.get(pk=loan_form.cleaned_data['account'].pk)
         # bank = Account.objects.get(pk=11) #The Bank
         debit_text = loan_form.cleaned_data['debit_text']
         credit_text = loan_form.cleaned_data['credit_text']
         is_loan = True
         transfer = Ledger.transfer(amount, loan_account, debit_text, account, credit_text, is_loan)
         print(transfer)
         return HttpResponseRedirect('/loans')
   else:
      loan_form = LoanForm()
      loan_form.fields['account'].queryset = request.user.customer.accounts
   context = {
      'user_id':user.id,
      'customers':Customer.objects.all(),
      'loan_form':loan_form,
      'accounts':Account.objects.all(),
      'ledger':Ledger.objects.all()
   }
   return render(request, 'bank_app/loans.html', context)

@login_required
def loan_details(request, id):
   account = Account.objects.filter(id=id)
   # transactions = Ledger.objects.filter(transaction_id=transaction_id)
   # print(transactions)
   if request.method == "POST":
      loan_form = LoanForm(request.POST)
      loan_form.fields['account'].queryset = request.user.customer.accounts
      if loan_form.is_valid():
         amount = loan_form.cleaned_data['amount']
         customer_account = Account.objects.get(pk=loan_form.cleaned_data['account'].pk)
         # account = Account.objects.get(pk=11) #The Bank
         account = Account.objects.get(pk=id)
         debit_text = loan_form.cleaned_data['debit_text']
         credit_text = loan_form.cleaned_data['credit_text']
         transfer = Ledger.transfer(amount, customer_account, debit_text, account, credit_text)
         print(transfer)
         return HttpResponseRedirect(f'/loan_details/{id}')
   else:
      loan_form = LoanForm()
      loan_form.fields['account'].queryset = request.user.customer.accounts

   context = {
      # 'transactions':transactions,
      'account':account,
      'accounts':Account.objects.all(),
      'loan_form':loan_form,
   }
   return render(request, 'bank_app/loan_details.html', context)

def send_request(request, url):
   session = requests.session()

   login_url = url + 'user/login/'
   session.get(login_url)
   csrf = session.cookies['csrftoken']

   bank_auth = {
      'user': 'laufey',
      'password': 'password',
      'csrfmiddlewaretoken' : csrf
   }

   response = session.post(url + 'user/login/', data=bank_auth)
   response.raise_for_status()
   csrf = session.cookies['csrftoken']
   
   headers = { 'X-CSRFToken' : csrf, 'Referer': url }
   response = session.post(url + 'external-transfer/', data=request.POST, headers=headers)
   response.raise_for_status()

   return response

@login_required
def transfer(request):
   if request.method == "POST":
      transfer_form = TransferForm(request.POST)
      transfer_form.fields['debit_account'].queryset = Account.objects.filter(user=request.user,account_type = 'Savings account' or 'Debit card' or 'Credit card')
      if transfer_form.is_valid():
         credit_bank_id = transfer_form.cleaned_data['credit_bank']
         credit_transfer_path = Bank.objects.get(pk=credit_bank_id).transfer_path
         debit_account = Account.objects.get(pk=transfer_form.cleaned_data['debit_account'].pk)
         debit_text = transfer_form.cleaned_data['debit_text']
         amount = transfer_form.cleaned_data['amount']

         if credit_bank_id == 1:
            credit_account = Account.objects.get(pk=transfer_form.cleaned_data['credit_account'])
            credit_text = transfer_form.cleaned_data['credit_text']
            transfer = Ledger.transfer(amount, debit_account, debit_text, credit_account, credit_text)
            print(transfer)
            account_sid = 'ACb82a519e91ea148938a5f8f69bd1d989'
            auth_token = 'd90ca1391c2a1ba2c0d9c38036787d1a'
            client = Client(account_sid, auth_token)
            number = Customer.objects.get(user_id=credit_account.user_id).phone_number
            message = client.messages \
                           .create(
                                 body=f"You got sent {amount} kr. from {request.user}. Explaination:{debit_text}",
                                 from_='+14782092875',
                                 to=f"{number}"
                           )
            print(message.sid)
            print(Customer.objects.get(user_id=credit_account.user_id).phone_number)
            return HttpResponseRedirect('/transfer')
         elif credit_bank_id == 2:
            credit_account = Account.objects.get(pk=11)
            credit_text = transfer_form.cleaned_data['credit_text']
            id = request.POST["credit_account"]
            print("id: ", id)
            # r = send_request(request, credit_transfer_path)
            #r = requests.post(credit_transfer_path, data=request.POST)
            # print(credit_transfer_path)
            # if r.status_code == 200:
            url = ("http://127.0.0.1:8000/api/v1/get-account/id=%s" % id)
            print("url: ", url)
            transfer = Ledger.externalTransfer(amount, debit_account, debit_text, credit_account, credit_text)
            print(transfer)
   else:
      transfer_form = TransferForm()
      transfer_form.fields['debit_account'].queryset = Account.objects.filter(user=request.user,account_type = 'Savings account' or 'Debit card' or 'Credit card')

      # print(transfer_form.fields['debit_account'].queryset)
   context = {
      'transfer_form':transfer_form
   }
   return render(request, 'bank_app/transfer.html', context)

@login_required
def profile(request):
   user = request.user
   update_user_form = UpdateUserForm(instance=user)
   if request.method == "POST":
      update_user_form = UpdateUserForm(request.POST, instance=user)
      if update_user_form.is_valid:
         update_user_form.save()

   context = {
      'update_user_form':update_user_form,
      'user_id':user.id,
      'customers':Customer.objects.all()
   }
   return render(request, 'bank_app/profile.html', context)

# Admin
@login_required
def staff(request):
   assert request.user.is_staff, 'Not for regular customers, only for admin'
   context = {
         'customers':Customer.objects.all(),
      }
   return render(request, 'bank_app/staff.html', context)

@login_required
def staffCustomerView(request):
   user = request.user
   assert request.user.is_staff, 'Not for regular customers, only for admin'
   context = {
      'user_id':user.id,
      'customers':Customer.objects.all(),
   }
   return render(request, 'bank_app/staffCustomerView.html', context)

@login_required
def staff_customer_details(request, id):
   assert request.user.is_staff, 'Not for regular customers, only for admin'
   user = User.objects.get(pk=id)
   customer = Customer.objects.get(user_id=user.id)
   update_customer_form = UpdateCustomerForm(instance=customer)
   update_user_form = UpdateUserForm(instance=user)
   if request.method == "POST":
         update_customer_form = UpdateCustomerForm(request.POST, instance=customer)
         update_user_form = UpdateUserForm(request.POST, instance=user)
         if update_customer_form.is_valid:
            update_customer_form.save()
         if update_user_form.is_valid:
            update_user_form.save()
   context = {
      'customer': user,
      'update_customer_form':update_customer_form,
      'update_user_form':update_user_form,
   }
   return render(request, 'bank_app/staff_customer_details.html', context)

@login_required
def staffAccountView(request):
   assert request.user.is_staff, 'Not for regular customers, only for admin'
   context = {
      'accounts':Account.objects.all(),
   }
   return render(request, 'bank_app/staffAccountView.html', context)

@login_required
def staffNewCustomer(request):
   assert request.user.is_staff, 'Not for regular customers, only for admin'
   if request.method == "POST":
      customer_form = createCustomer(request.POST)
      user_form = createUser(request.POST)
      if user_form.is_valid() and customer_form.is_valid():
         username = user_form.cleaned_data['username']
         first_name = user_form.cleaned_data['first_name']
         last_name = user_form.cleaned_data['last_name']
         email = user_form.cleaned_data['email']
         password = user_form.cleaned_data['password']
         phone_number = customer_form.cleaned_data['phone_number']
         customer_rank = customer_form.cleaned_data['customer_rank']
         user = User.objects.create_user(
            username=username, 
            first_name=first_name, 
            last_name=last_name, 
            email=email, 
            password=password)
         print(f'New customer with username: {username} and email: {email}')
         Customer.objects.create(user=user, phone_number=phone_number, customer_rank=customer_rank)
   context = {
      'customer_form':createCustomer,
      'user_form':createUser,
      'customers':Customer.objects.all(),
   }
   return render(request, 'bank_app/staffNewCustomer.html', context)

@login_required
def staffNewAccount(request):
   assert request.user.is_staff, 'Not for regular customers, only for admin'
   user=request.user
   if request.method == "POST":
      account_form = createAccount(request.POST)
      if account_form.is_valid():
         Account.objects.create(user=account_form.cleaned_data['user'], title=account_form.cleaned_data['title'])
   context = {
         'account_form':createAccount,
         'accounts':Account.objects.all(),
         'user_id':user.id,
         'customers':Customer.objects.all(),
      }
   return render(request, 'bank_app/staffNewAccount.html', context)

@login_required
def staffTransfers(request):
   assert request.user.is_staff, 'Not for regular customers, only for admin'
   transfer_form = TransferForm()
   # transfer_form.fields['debit_account'].queryset = request.user.customer.accounts
   if request.method == "POST":
      transfer_form = TransferForm(request.POST)
      if transfer_form.is_valid():
         debit_account = Account.objects.get(pk=transfer_form.cleaned_data['debit_account'])
         credit_account = Account.objects.get(pk=transfer_form.cleaned_data['credit_account'])
         amount = transfer_form.cleaned_data['amount']
         transfer = Ledger.transfer(amount, debit_account, credit_account)
         print(transfer)
   else:
      transfer_form = TransferForm()
   context = {
      'transfer_form':TransferForm
   }  
   
   return render(request, 'bank_app/staffTransfers.html', context)



class TransferView(View):
   queryset = Ledger.objects.all()

   permission_classes = [permissions.IsAuthenticated]

   test = "test"

   def get(self, request, *args, **kwargs):
      return HttpResponse(self.test)

   def post(self, request, *args, **kwargs):

      transfer_form = TransferForm(request.POST)
      transfer_form.fields['debit_account'].queryset = request.user.customer.accounts
      if transfer_form.is_valid():
         credit_account = Account.objects.get(pk=transfer_form.cleaned_data['credit_account'])
         credit_text = transfer_form.cleaned_data['credit_text']
         amount = transfer_form.cleaned_data['amount']
         transfer = ExternalLedger.transfer(amount, credit_account, credit_text, False)
         print(transfer)
         return HttpResponse(self.test)
      
      return HttpResponse(status=400)