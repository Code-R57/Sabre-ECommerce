from django.contrib import admin
from django.urls import path, include
from ecomm import views

urlpatterns = [
    path('admin', admin.site.urls, name="admin"),
    path('', views.index, name="login"),
    path('login', views.loginUser, name="login"),
    path('logout', views.logoutUser, name="logout"),
]