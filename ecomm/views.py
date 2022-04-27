from urllib import request
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.contrib.auth import logout
from django.views import View
import mysql.connector as sql
from soupsieve import select
from sabre import settings

database = settings.DATABASES
connection = sql.connect(host = database['default']['HOST'], user = database['default']['USER'], password = database['default']['PASSWORD'], database = database['default']['NAME'])
cursor = connection.cursor()

username = ""
cart_quantity = 0

# Create your views here.
def index(request):
    return render(request, 'login.html', {'error': ""})

def loginUser(request):
    if request.method=="POST":
        global username
        global cart_quantity
        password = ""

        data = request.POST
        for key, value in data.items():
            if key=="username":
                username = value
            if key=="password":
                password = value
        
        query = "SELECT * FROM USER WHERE UserID = '{}' AND Password = '{}'".format(username, password)
        cursor.execute(query)

        value = tuple(cursor.fetchall())

        if value == ():
            return render(request, "login.html", {'error': "Username or password is invalid"})
        else:
            return render(request, "main.html", {'cart_items_num': cart_quantity})

def register(request):
    return render(request, 'register.html', {'error': ""})

def registerUser(request):
    global username
    global cart_quantity
    name = ""
    password = ""
    locality = ""
    street = ""
    pin = ""

    if request.method=="POST":
        data=request.POST
        for key,value in data.items():
            if key=="username":
                username=value
            if key=="name":
                name=value
            if key=="password":
                password=value
            if key=="locality":
                locality=value
            if key=="street":
                street=value
            if key=="pin":
                pin=value
        
        query = "SELECT * FROM USER WHERE UserID = '{}'".format(username)
        cursor.execute(query)
        value = tuple(cursor.fetchall())

        if value == ():
            query = "insert into user Values('{}','{}','{}','{}','{}','{}')".format(username,name,password,locality,street,pin)
            cursor.execute(query)
            connection.commit()

            cart_quantity = 0
            return render(request,'main.html', {'cart_items_num': cart_quantity})
        else:
            return render(request, 'register.html', {'error': 'Username taken'})

class Cart:
    def __init__(self, pid):
        query = "SELECT * FROM PRODUCT WHERE ProductID = '{}'".format(pid)
        cursor.execute(query)
        product = tuple(cursor.fetchall())
        self.name = product[0][1]
        self.price = product[0][4]
        query_cart = "SELECT Quantity FROM CART WHERE ProductID = '{}'".format(pid)
        cursor.execute(query_cart)
        prod = tuple(cursor.fetchall())
        self.quant_price = prod[0][3] * product[0][4]
    
def addToCart(request, pid, sid, quant):
        global cart_quantity
        global username
        query_check = "SELECT * FROM CART WHERE ProductID = '{}'".format(pid)
        cursor.execute(query_check)
        check = tuple(cursor.fetchall())

        if check==():
            query = "insert into cart Values('{}', '{}', '{}', '{}')".format(username, sid, pid, quant)
            cursor.execute(query)
            connection.commit()
        else:
            query = "UPDATE CART SET Quantity = '{}' WHERE ProductID = '{}'".format(check[0][3], pid)
            cursor.execute(query)
            connection.commit()

        #add sellerID options in productdescription.html
        query_quant = "select sum(quantity) from cart where UserID = '{}'".format(username)
        cursor.execute(query_quant)
        cart_quantity = int(cursor.fetchall())
        return HttpResponseRedirect('/productdescription/?{}'.format(pid))


def home(request):
    global cart_quantity
    return render(request, 'main.html', {'cart_items_num': cart_quantity})

def cart(request):
    global cart_quantity
    query = "SELECT ProductID FROM CART"
    cursor.execute(query)
    cart_pids = tuple(cursor.fetchall())
    cart_items = []
    total = 0
    for pid in cart_pids:
        item = Cart(int(pid))
        cart_items.append(item)
        total += item.quant_price
    return render(request, 'cart.html', {'cart_items_num': cart_quantity, 'cart_items': cart_items, 'total': total})

def confirmation(request):
    global cart_quantity
    return render(request, 'confirmation.html', {'cart_items_num': cart_quantity})

def productdescription(request, pid):
    global cart_quantity
    global username
    query = "SELECT * FROM PRODUCT WHERE ProductID = '{}'".format(pid)
    cursor.execute(query)
    product = tuple(cursor.fetchall())
    name = product[0][1]
    price = product[0][4]
    query_cat = "SELECT CategoryName FROM CATEGORY WHERE CategoryID = '{}'".format(product[0][5])
    cursor.execute(query_cat)
    category = str(cursor.fetchall())
    return render(request, 'productdescription.html', {'cart_items_num': cart_quantity, 'name': name, 'price': price, 'category': category})

def checkout(request):
    global cart_quantity
    return render(request, 'checkout.html', {'cart_items_num': cart_quantity})

def logoutUser(request):
    return redirect("/login")
