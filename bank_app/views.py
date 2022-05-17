from multiprocessing import context
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from .models import Account, Customer, Ledger
from django.contrib.auth.models import User
from .forms import createAccount, createCustomer, createUser, UpdateUserForm, UpdateCustomerForm, TransferForm
from decimal import Decimal


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
      'form':createAccount,
      'accounts':Account.objects.all(),
      'user_id':user.id,
      }
   return render(request, 'bank_app/accounts.html', context)

@login_required
def loans(request):
   context = {
      'customers':Customer.objects.all(),
   }
   return render(request, 'bank_app/loans.html', context)
   
@login_required
def transfer(request):
   transfer_form = TransferForm()
   transfer_form.fields['debit_account'].queryset = request.user.customer.accounts
   if request.method == "POST":
      transfer_form = TransferForm(request.POST)
      if transfer_form.is_valid():
         debit_account = Account.objects.get(pk=transfer_form.cleaned_data['debit_account'])
         credit_account = Account.objects.get(pk=transfer_form.cleaned_data['credit_account'])

         amount = transfer_form.cleaned_data['amount']
         print(debit_account)
         print(credit_account)
         print(amount)
         transfer = Ledger.transfer(amount, debit_account, credit_account)
         print(transfer)
   else:
      transfer_form = TransferForm()
      print("HeLLO")
      # print(transfer_form.fields['debit_account'].queryset)
   context = {
      'transfer_form':TransferForm
   }
   return render(request, 'bank_app/transfer.html', context)

@login_required
def profile(request):
   user = request.user
   print(user)
   update_user_form = UpdateUserForm(instance=user)
   if request.method == "POST":
      update_user_form = UpdateUserForm(request.POST, instance=user)
      if update_user_form.is_valid:
         update_user_form.save()

   context = {
      'update_user_form':UpdateUserForm,
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
   if request.method == "POST":
      update_customer_form = UpdateCustomerForm(request.POST, instance=request.user.customer)
      if update_customer_form.is_valid:
         update_customer_form.save()
   context = {
      'update_customer_form':UpdateCustomerForm,
      'user_id':user.id,
      'customers':Customer.objects.all(),
   }
   return render(request, 'bank_app/staffCustomerView.html', context)

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
      print("NEW CUSTOMER ALERT")
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
         print(f'Username: {username} - email: {email}')
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
      print("Hello")
      account_form = createAccount(request.POST)
      if account_form.is_valid():
         Account.objects.create(user=account_form.cleaned_data['user'], title=account_form.cleaned_data['title'])
         print(user)
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
   print(request.user.customer.accounts)
   print(transfer_form.fields['debit_account'])
   if request.method == "POST":
      transfer_form = TransferForm(request.POST)
      if transfer_form.is_valid():
         debit_account = Account.objects.get(pk=transfer_form.cleaned_data['debit_account'])
         credit_account = Account.objects.get(pk=transfer_form.cleaned_data['credit_account'])
         amount = transfer_form.cleaned_data['amount']
         print(debit_account.pk)
         # print(credit_account)
         print(amount)
         transfer = Ledger.transfer(amount, debit_account, credit_account)
         print(transfer)
   else:
      transfer_form = TransferForm()
   context = {
      'transfer_form':TransferForm
   }  
   
   return render(request, 'bank_app/staffTransfers.html', context)
