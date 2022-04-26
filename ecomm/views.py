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
    return render(request, 'login.html')

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
            return render(request, "login.html")
        else:
            return render(request, "main.html")

    return render(request, "error.html")

def register(request):
    return render(request, 'register.html')

def registerUser(request):
    global username
    name=""
    password=""
    locality=""
    street=""
    pin=""
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
        
        query = "insert into user Values('{}','{}','{}','{}','{}','{}')".format(username,name,password,locality,street,pin)
        cursor.execute(query)
        connection.commit()

    return render(request,'main.html')

def home(request):
    return render(request, 'main.html')

def cart(request):
    return render(request, 'cart.html')

def confirmation(request):
    return render(request, 'confirmation.html')

def productdescription(request):
    return render(request, 'productdescription.html')

def checkout(request):
    return render(request, 'checkout.html')

def logoutUser(request):
    logout(request)
    return redirect("/login")
