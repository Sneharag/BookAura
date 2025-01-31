from django.shortcuts import render,redirect

from django.views.generic import View

from bookapp.forms import SignUpForm,LoginForm,OrderForm

from bookapp.models import User,Book,BasketItem,OrderItem,Order

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
    

class BookDetailView(View):

    template_name="book_detail.html"

    def get(self,request,*args,**kwargs):

        id=kwargs.get("pk")

        qs=Book.objects.get(id=id)

        return render(request,self.template_name,{"data":qs})
    
class AddtoCartView(View):

    def post(self,request,*args,**kwargs):

        id=kwargs.get("pk")

        quantity=request.POST.get("quantity")

        book_object=Book.objects.get(id=id)

        basket_object=request.user.cart

        BasketItem.objects.create(
            book_object=book_object,
            quantity=quantity,
            basket_object=basket_object
        )

        print("Item has been added to Cart")

        return redirect("cart-summary")

class CartSummaryView(View):

    template_name="cart_summary.html"

    def get(self,request,*args,**kwargs):

        qs=BasketItem.objects.filter(basket_object=request.user.cart,is_order_placed=False)

        basket_item_count=qs.count()

        basket_total=sum([bi.item_total for bi in qs])

        return render(request,self.template_name,{"basketitems":qs,"basket_total":basket_total,"basket_item_count":basket_item_count})

class BasketItemDeleteView(View):

    def get(self,request,*args,**kwargs):

        id=kwargs.get("pk")

        basket_item=BasketItem.objects.filter(id=id,basket_object=request.user.cart)

        basket_item.delete()

        return redirect("cart-summary")
    
class PlaceOrderView(View):

    template_name="place_order.html"

    form_class=OrderForm

    def get(self,request,*args,**kwargs):

        form_instance=self.form_class()

        qs=request.user.cart.cart_item.filter(is_order_placed=False)

        total=sum([bi.item_total for bi in qs])

        return render(request,self.template_name,{"form":form_instance,"items":qs,"total":total})
    
    def post(self,request,*args,**kwargs):

        form_data=request.POST

        form_instance=self.form_class(form_data)

        if form_instance.is_valid():

            form_instance.instance.customer=request.user

            order_instance=form_instance.save()

            basket_items=request.user.cart.cart_item.filter(is_order_placed=False)

            for bi in basket_items:

                OrderItem.objects.create(

                    order_object=order_instance,
                    book_object=bi.book_object,
                    quantity=bi.quantity,
                    price=bi.book_object.price
                )

                bi.is_order_placed=True

                bi.save()

        return redirect("order-summary")

class OrderSummaryView(View):

    template_name="order_summary.html"

    def get(self,request,*args,**kwargs):

        qs=request.user.orders.all()

        return render(request,self.template_name,{"orders":qs})
            

