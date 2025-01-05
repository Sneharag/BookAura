from django import forms

from django.contrib.auth.forms import UserCreationForm

from bookapp.models import User

class SignUpForm(UserCreationForm):

    class Meta:

        model=User

        fields=["username","email","password1","password2","phone"]


class LoginForm(forms.Form):

    username=forms.CharField(widget=forms.TextInput(attrs={"class":"form-control mb-3"}))

    password=forms.CharField(widget=forms.TextInput(attrs={"class":"form-control mb-3"}))

