from dataclasses import fields
from email.policy import default
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
    fields = ('user', 'phone_number', 'customer_rank')

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
    fields = ('title', 'user')
    # title = forms.CharField(max_length = 200)
    # user = forms.CharField(max_length=200)


# Not in use I THINK

class UserForm(forms.ModelForm):
    username = forms.CharField(label='Username', disabled=True)
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email')
  