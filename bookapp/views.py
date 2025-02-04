from django.shortcuts import render,redirect,get_object_or_404

from django.views.generic import View,TemplateView

from bookapp.forms import SignUpForm,LoginForm,OrderForm,UserProfileForm,AddressForm

from bookapp.models import User,Book,BasketItem,OrderItem,Order,WishlistItem,Address,Category

from django.core.mail import send_mail

from django.contrib import messages

from django.contrib.auth import authenticate,login,logout

from django.views.decorators.csrf import csrf_exempt

from django.utils.decorators import method_decorator

from django.contrib import messages

from bookapp.decorators import signin_required

from django.db.models import Q

from django.views.decorators.cache import never_cache

from decouple import config

decs=[signin_required,never_cache]

RZP_KEY_ID=config('RZP_KEY_ID')

RZP_KEY_SECRET=config('RZP_KEY_SECRET')

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
    
class BooksView(View):

    template_name="books.html"

    def get(self,request,*args,**kwargs):

        category = request.GET.get('category')  
    
        categories = Category.objects.all()

        search_text=request.GET.get("filter")
    
        if category:
        
            books = Book.objects.filter(category_object=category) 
        else:
            
            books = Book.objects.all() 

        if search_text:

            books=books.filter(Q(title__contains=search_text)|Q(language__contains=search_text)|Q(author__contains=search_text))

        return render(request,self.template_name,{"data":books,'categories': categories,
                    'selected_category': int(category) if category else None})

@method_decorator(decs,name="dispatch")
class BookDetailView(View):

    template_name="book_detail.html"

    def get(self,request,*args,**kwargs):

        id=kwargs.get("pk")

        qs=Book.objects.get(id=id)

        return render(request,self.template_name,{"data":qs})
    
@method_decorator(decs,name="dispatch")
class AddtoCartView(View):

    def post(self,request,*args,**kwargs):

        id=kwargs.get("pk")

        quantity=request.POST.get("quantity",1)

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

@method_decorator(decs,name="dispatch")
class BasketItemDeleteView(View):

    def get(self,request,*args,**kwargs):

        id=kwargs.get("pk")

        basket_item=BasketItem.objects.filter(id=id,basket_object=request.user.cart)

        basket_item.delete()

        return redirect("cart-summary")
    
import razorpay
@method_decorator(decs,name="dispatch")
class PlaceOrderView(View):

    template_name="place_order.html"

    form_class=OrderForm

    def get(self,request,*args,**kwargs):

        form_instance=self.form_class()

        user_profile = request.user.userprofile

        addresses = Address.objects.filter(user_profile=user_profile)

        qs=request.user.cart.cart_item.filter(is_order_placed=False)

        total=sum([bi.item_total for bi in qs])

        return render(request,self.template_name,{"form":form_instance,"items":qs,"total":total,"addresses":addresses})
    
    def post(self,request,*args,**kwargs):

        form_data=request.POST

        form_instance=self.form_class(form_data)

        if form_instance.is_valid():

            form_instance.instance.customer=request.user

            selected_address_id=form_data.get("selected_address")

            selected_address=Address.objects.get(id=selected_address_id,user_profile=request.user.userprofile)

            order_instance=form_instance.save(commit=False)

            order_instance.address=selected_address

            order_instance.save()

            basket_items=request.user.cart.cart_item.filter(is_order_placed=False)

            payment_method=form_instance.cleaned_data.get("payment_method")
            print(payment_method)

            for bi in basket_items:

                OrderItem.objects.create(

                    order_object=order_instance,
                    book_object=bi.book_object,
                    quantity=bi.quantity,
                    price=bi.book_object.price
                )

                bi.is_order_placed=True

                bi.save()

            if payment_method=="ONLINE":

                client=razorpay.Client(auth=(RZP_KEY_ID,RZP_KEY_SECRET))

                total=sum([bi.item_total for bi in basket_items])*100

                data={"amount":total,"currency":"INR","receipt":"order_rcpid_11"}

                payment=client.order.create(data=data)

                rzp_order_id=payment.get("id")

                order_instance.rzp_order_id=rzp_order_id

                order_instance.save()

                context={
                    "amount":total,
                    "currency":"INR",
                    "key_id":RZP_KEY_ID,
                    "order_id":rzp_order_id
                }

                return render(request,"payment.html",context)

        return redirect("book-list")

class OrderSummaryView(View):

    template_name="order_summary.html"

    def get(self,request,*args,**kwargs):

        qs=request.user.orders.all().order_by("-created_at")

        return render(request,self.template_name,{"orders":qs})

@method_decorator([csrf_exempt],name="dispatch")
class PaymentVerificationView(View):

    def post(self,request,*args,**kwargs):

        client = razorpay.Client(auth=(RZP_KEY_ID, RZP_KEY_SECRET))

        try:
            client.utility.verify_payment_signature(request.POST)
            print("payment success")

            order_id=request.POST.get("razorpay_order_id")

            order_object=Order.objects.get(rzp_order_id=order_id)

            order_object.is_paid=True

            order_object.save()

            login(request,order_object.customer)

        except:

            print("payment failed")


        return redirect("order-summary")

class UserProfileView(View):

    template_name='profile.html'

    form_class=UserProfileForm

    def get(self, request,*args,**kwargs):

        form_instance = self.form_class(instance=request.user)

        context = {
            'form': form_instance,
            'addresses': request.user.userprofile.addresses.all() 
        }

        return render(request, self.template_name, context)

    def post(self, request,*args,**kwargs):

        form_data=request.POST

        form_instance = self.form_class(form_data, instance=request.user)

        if form_instance.is_valid():

            form_instance.save()  

            return redirect('user-profile')
        
        context = {
            'form': form_instance,
            'addresses': request.user.userprofile.addresses.all()
        }
        return render(request, self.template_name, context)

class AddressCreateView(View):

    template_name='addressadd.html'

    form_class=AddressForm

    def get(self, request,*args,**kwargs):

        form_instance=self.form_class()
        
        return render(request,self.template_name, {'form': form_instance})

    def post(self, request,*args,**kwargs):

        form_data=request.POST

        form_instance = self.form_class(form_data)

        if form_instance.is_valid():
            
            address = form_instance.save(commit=False)

            user_profile=request.user.userprofile

            address.user_profile= user_profile

            address.save()

            return redirect('user-profile')  
        
        return render(request, self.template_name, {'form': form_instance})

class AddressDeleteView(View):

    def get(self,request,*args,**kwargs):

        id=kwargs.get("pk")

        address = Address.objects.get(id=id,user_profile=request.user.user_profile)

        address.delete()

        return redirect("user-profile")

@method_decorator(decs,name="dispatch")
class AddtoWishListView(View):

    def post(self,request,*args,**kwargs):

        id=kwargs.get("pk")

        book_object=get_object_or_404(Book,id=id)

        if request.user.wishlist:

            wishlist_object=request.user.wishlist

            WishlistItem.objects.create(
            book_object=book_object,
            wishlist_object=wishlist_object
            )

        return redirect("book-detail",pk=book_object.id)
    
@method_decorator(decs,name="dispatch")
class WishListView(View):

    template_name='wishlist.html'

    def get(self,request,*args,**kwargs):

        wishlist_object = request.user.wishlist

        qs = wishlist_object.wishlist_item.all() if wishlist_object else []

        return render(request,self.template_name,{"wishlistitems":qs})
    
class WishListDelete(View):

    def get(self,request,*args,**kwargs):

        id=kwargs.get("pk")

        wishlist_item=WishlistItem.objects.filter(id=id,wishlist_object=request.user.wishlist)

        wishlist_item.delete()

        return redirect("wishlist")


class SignOutView(View):

    def get(self,request,*args,**kwargs):

        logout(request)

        return redirect("signin")

class AboutPageView(TemplateView):

    template_name = 'about.html'


