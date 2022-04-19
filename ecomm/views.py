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

def logoutUser(request):
    logout(request)
    return redirect("/login")