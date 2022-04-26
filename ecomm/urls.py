from django.contrib import admin
from django.urls import path, include
from ecomm import views

urlpatterns = [
    path('admin', admin.site.urls, name="admin"),
    path('', views.index, name="login"),
    path('login', views.loginUser, name="login"),
    path('logout', views.logoutUser, name="logout"),
    path('register', views.register, name="register"),
    path('registerUser', views.registerUser, name="registerUser"),
    path('home',views.home, name="home"),
    path('cart',views.cart, name="cart"),
    path('confirmation',views.confirmation, name="confirmation"),
    path('checkout',views.checkout, name="checkout"),
    path('productdescription',views.productdescription, name="productdescription")
]