from django.contrib import admin
from django.urls import path
from ecomm import views

urlpatterns = [
    path('admin', admin.site.urls, name="admin"),
    path('', views.index, name="login"),
    path('login', views.loginUser, name="loginUser"),
    path('logout', views.logoutUser, name="logout"),
    path('register', views.register, name="register"),
    path('registerUser', views.registerUser, name="registerUser"),
    path('home',views.home, name="home"),
    path('cart',views.cart, name="cart"),
    path('confirmation',views.confirmation, name="confirmation"),
    path('search',views.search, name="search"),
    path('placeOrder',views.placeOrder, name="placeOrder"),
    path('user/<str:uid>',views.user, name="user"),
    path('seller/<str:sid>',views.seller, name="seller"),
    path('addProduct/<str:sid>', views.addProduct, name="addProduct"),
    path('updateQuantity/<str:sid>', views.updateQuantity, name="updateQuantity"),
    path('productdescription/<int:pid>',views.productdescription, name="productdescription"),
    path('addToCart/<int:pid>', views.addToCart, name='addToCart')
]