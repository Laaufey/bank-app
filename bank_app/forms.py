from dataclasses import fields
from email.policy import default
from logging import PlaceHolder
from urllib import request
from django import forms
from django.contrib.auth.models import User
from .models import Account
from .models import Customer


class createCustomer(forms.ModelForm):
  class Meta:
    model = Customer
    fields = ('phone_number', 'customer_rank')

class UpdateCustomerForm(forms.ModelForm):

  class Meta:
    model = Customer
    fields = ('phone_number', 'customer_rank')

class createUser(forms.ModelForm):
  class Meta:
    model = User
    fields = ('first_name', 'last_name', 'username', 'email', 'password')

class UpdateUserForm(forms.ModelForm):
  username = forms.CharField(required=False)
  class Meta:
    model = User
    fields = ('first_name', 'last_name', 'username', 'email')

class createAccount(forms.ModelForm):
  class Meta:
    model = Account
    fields = ('title', 'user', 'account_type')
    # title = forms.CharField(max_length = 200)
    # user = forms.CharField(max_length=200)

class TransferForm(forms.Form):
  amount = forms.DecimalField(max_digits=10)
  debit_account = forms.ModelChoiceField(label='Debit Account', queryset=Customer.objects.none())
  debit_text = forms.CharField(max_length=35, label="Note:")
  credit_bank = forms.IntegerField(label='Bank Number')
  credit_account = forms.IntegerField(label='Credit Account Number')
  credit_text = forms.CharField(max_length=35, label="Explanaition:")

  def clean(self):
      super().clean()
      credit_account = self.cleaned_data.get('credit_account')
      Account.objects.get(pk=credit_account)
      return self.cleaned_data


class LoanForm(forms.Form):
  amount = forms.DecimalField(max_digits=10)
  period = forms.CharField()
  account = forms.ModelChoiceField(label='Choose account', queryset=Customer.objects.none())
  debit_text = forms.CharField(max_length=35)
  credit_text = forms.CharField(max_length=35)

  def clean(self):
    super().clean()
    return self.cleaned_data
  
class PaymentForm(forms.Form):
  amount = forms.DecimalField(max_digits=10)
  period = forms.CharField()
  customer_account = forms.ModelChoiceField(label='Choose account', queryset=Customer.objects.none())
  debit_text = forms.CharField(max_length=35)
  credit_text = forms.CharField(max_length=35)

  def clean(self):
    super().clean()
    return self.cleaned_data
# Not in use I THINK

class UserForm(forms.ModelForm):
    username = forms.CharField(label='Username', disabled=True)
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email')
