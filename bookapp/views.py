from django.shortcuts import render,redirect

from django.views.generic import View

from bookapp.forms import SignUpForm,LoginForm

from bookapp.models import User,Book

from django.core.mail import send_mail

from django.contrib import messages

from django.contrib.auth import authenticate,login,logout

def send_otp_email(user):

    user.generate_otp()

    subject="Verify your email"

    message=f"otp for account verification is {user.otp}"

    from_email="sneharag101@gmail.com"

    to_email=[user.email]

    send_mail(subject,message,from_email,to_email)

class SignUpView(View):

    template_name="register.html"

    form_class=SignUpForm

    def get(self,request,*args,**kwargs):

        form_instance=self.form_class()

        return render(request,self.template_name,{"form":form_instance})
    
    def post(self,request,*args,**kwargs):

        form_data=request.POST

        form_instance=self.form_class(form_data)

        if form_instance.is_valid():

            user_object=form_instance.save(commit=False)

            user_object.is_active=False

            user_object.save()

            send_otp_email(user_object)

            return redirect("verify-email")
        
        return render(request,self.template_name,{"form":form_instance})

class VerifyEmailView(View):

    template_name="verify_email.html"

    def get(self,request,*args,**kwargs):

        return render(request,self.template_name)
    
    def post(self,request,*args,**kwargs):

        otp=request.POST.get("otp")

        try:

            user_object=User.objects.get(otp=otp)

            user_object.is_active=True

            user_object.is_verified=True

            user_object.otp=None
        
            user_object.save()

            return redirect("signin")
        
        except:

            messages.error(request,"Invalid otp")

        return render(request,self.template_name)

class LogInView(View):

    template_name="signin.html"

    form_class=LoginForm

    def get(self,request,*args,**kwargs):

        form_instance=self.form_class()

        return render(request,self.template_name,{"form":form_instance})
    
    def post(self,request,*args,**kwargs):

        form_data=request.POST

        form_instance=self.form_class(form_data)

        if form_instance.is_valid():

            uname=form_instance.cleaned_data.get("username")

            pwd=form_instance.cleaned_data.get("password")

            user_object=authenticate(request,username=uname,password=pwd)

            if user_object:

                login(request,user_object)

                return redirect("book-list")
            
        return render(request,self.template_name,{"form":form_instance})


class BookListView(View):

    template_name="index.html"

    def get(self,request,*args,**kwargs):

        qs=Book.objects.all()

        return render(request,self.template_name,{"data":qs})
    



