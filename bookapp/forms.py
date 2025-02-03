from django import forms

from django.contrib.auth.forms import UserCreationForm

from bookapp.models import User,Order,UserProfile,Address

class SignUpForm(UserCreationForm):

    class Meta:

        model=User

        fields=["username","email","password1","password2","phone"]


class LoginForm(forms.Form):

    username=forms.CharField(widget=forms.TextInput(attrs={"class":"form-control mb-3"}))

    password=forms.CharField(widget=forms.PasswordInput(attrs={"class":"form-control mb-3"}))

class UserProfileForm(forms.ModelForm):

    class Meta:

            model=User

            fields=['username','email','phone']

class AddressForm(forms.ModelForm):
     
     class Meta:
          
          model=Address

          fields=['street','city','state','pincode','country']


class OrderForm(forms.ModelForm):

    class Meta:

        model=Order

        fields=["address","phone","payment_method"]

