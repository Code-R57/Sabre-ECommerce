from django.shortcuts import render, redirect
from django.contrib.auth import logout
import mysql.connector as sql
from sabre import settings

database = settings.DATABASES
connection = sql.connect(host = database['default']['HOST'], user = database['default']['USER'], password = database['default']['PASSWORD'], database = database['default']['NAME'])
cursor = connection.cursor()

username = ""

# Create your views here.
def index(request):
    return render(request, 'login.html', {'error': ""})

def loginUser(request):
    if request.method=="POST":
        global username
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
            if request.session['cart_items_num'] == None:
                request.session['cart_items_num'] = 0
            return render(request, "main.html", {'cart_items_num': request.session['cart_items_num']})

def register(request):
    return render(request, 'register.html', {'error': ""})

def registerUser(request):
    global username
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
            if request.session['cart_items_num'] == None:
                request.session['cart_items_num'] = 0
            return render(request,'main.html', {'cart_items_num': request.session['cart_items_num']})
        else:
            return render(request, 'register.html', {'error': 'Username taken'})

def addToCart(request):
    request.session['cart_items_num'] += 1
    return render(request, 'productdescription.html', {'cart_items_num': request.session['cart_items_num']})

def home(request):
    return render(request, 'main.html', {'cart_items_num': request.session['cart_items_num']})

def cart(request):
    return render(request, 'cart.html', {'cart_items_num': request.session['cart_items_num']})

def confirmation(request):
    return render(request, 'confirmation.html', {'cart_items_num': request.session['cart_items_num']})

def productdescription(request):
    return render(request, 'productdescription.html', {'cart_items_num': request.session['cart_items_num']})

def checkout(request):
    return render(request, 'checkout.html', {'cart_items_num': request.session['cart_items_num']})

def logoutUser(request):
    logout(request)
    return redirect("/login")
