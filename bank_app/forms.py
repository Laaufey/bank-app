from django import forms



class createAccount(forms.Form):
    title = forms.CharField(max_length = 200)