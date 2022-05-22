from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django import forms



# Not in user I think
class signup_form(UserCreationForm):
  email = forms.EmailField()
  first_name = forms.CharField(max_length=50)
  last_name = forms.CharField(max_length=50)

  class Meta:
    model = User
    fields = ('username', 'first_name', 'last_name', 'email', 'password', 'password2')

