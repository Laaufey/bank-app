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


class TransferForm(forms.Form):
  amount = forms.DecimalField(max_digits=10)
  debit_account = forms.ModelChoiceField(label='Debit Account', queryset=Customer.objects.none())
  debit_text = forms.CharField(max_length=35, label="Note:")
  credit_bank = forms.IntegerField(label='Bank Number')
  credit_account = forms.IntegerField(label='Credit Account Number')
  credit_text = forms.CharField(max_length=35, label="Explanaition:")

  def clean(self):
      super().clean()
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


class TickerForm(forms.Form):
    ticker = forms.CharField(label='', max_length=5)
    ticker.widget.attrs['placeholder'] = "Search by ticker"

class StockForm(forms.Form):
    stock_amount = forms.IntegerField(label='Number of shares')
    stock_amount.widget.attrs['placeholder'] = "Number of shares"
    debit_account = forms.ModelChoiceField(
        label='Choose payment account', queryset=Customer.objects.none())

    def clean(self):
        super().clean()
        return self.cleaned_data

class SellStockForm(forms.Form):
    stock_holdings = forms.ModelChoiceField(
        label='Choose Stock Holding', queryset=Customer.objects.none())
    debit_account = forms.ModelChoiceField(
        label='Receive payment account', queryset=Customer.objects.none())
