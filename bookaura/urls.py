"""
URL configuration for bookaura project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from bookapp import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("admin/", admin.site.urls),
    path("signup/",views.SignUpView.as_view(),name="signup"),
    path("verify/otp/",views.VerifyEmailView.as_view(),name="verify-email"),
    path("",views.LogInView.as_view(),name="signin"),
    path("signout/",views.SignOutView.as_view(),name="signout"),

    path("index/",views.BookListView.as_view(),name="book-list"),
    path("shop/",views.BooksView.as_view(),name="books"),
    path("profile/",views.UserProfileView.as_view(),name='user-profile'),
    path("profile/addaddress/",views.AddressCreateView.as_view(),name="add-address"),
    path("deleteaddress/<int:pk>/",views.AddressDeleteView.as_view(),name="delete-address"),

    path("books/<int:pk>/",views.BookDetailView.as_view(),name="book-detail"),
    path("books/<int:pk>/cart/add/",views.AddtoCartView.as_view(),name="addtocart"),
    path("wishlist/add/<int:pk>/",views.AddtoWishListView.as_view(),name='addtowishlist'),
    path("wishlist/",views.WishListView.as_view(),name='wishlist'),
    path("wishlist/remove/<int:pk>/",views.WishListDelete.as_view(),name='wishlist-delete'),
    path('about/', views.AboutPageView.as_view(), name='about'),

    path("cart/summary/",views.CartSummaryView.as_view(),name='cart-summary'),
    path("books/<int:pk>/remove/",views.BasketItemDeleteView.as_view(),name="book-delete"),
    path("place/order/",views.PlaceOrderView.as_view(),name="place-order"),

    path("order/summary/",views.OrderSummaryView.as_view(),name="order-summary"),
    path("payment/verify/",views.PaymentVerificationView.as_view(),name="payment-verify"),
    
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
