from urllib import request
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.contrib.auth import logout
from django.views import View
import mysql.connector as sql
from sabre import settings
from datetime import date

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
            query = "SELECT * FROM SELLER WHERE SellerID = '{}' AND Password = '{}'".format(username, password)
            cursor.execute(query)

            seller = tuple(cursor.fetchall())

            if seller == ():
                return render(request, "login.html", {'error': "Username or password is invalid"})
            else:
                return redirect("/seller/"+username)
        else:
            return redirect("/home")

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
    
def addToCart(request, pid):
    global cart_quantity
    global username

    sid = ""
    quantity = 0

    if request.method=="POST":
        data=request.POST
        for key,value in data.items():
            print(key)
            print(value)
            if key=="qty":
                quantity = value
            if key=="sellers":
                sid = value

    query_check = "SELECT * FROM CART WHERE ProductID = '{}' AND SellerID = '{}'".format(pid, sid)
    cursor.execute(query_check)
    check = tuple(cursor.fetchall())

    if check==():
        query = "insert into cart Values('{}', '{}', '{}', '{}')".format(username, sid, pid, quantity)
        cursor.execute(query)
        connection.commit()
    else:
        query = "UPDATE CART SET Quantity = Quantity+'{}' WHERE ProductID = '{}' AND SellerID = '{}'".format(quantity, pid, sid)
        cursor.execute(query)
        connection.commit()

    query = "UPDATE SELLER_PRODUCT SET Quantity = Quantity - {} WHERE ProductID = '{}' AND SellerID = '{}'".format(quantity, pid, sid)
    cursor.execute(query)
    connection.commit()

    query_quant = "select count(*) from cart where UserID = '{}'".format(username)
    cursor.execute(query_quant)
    cart_quantity = (tuple(cursor.fetchall()))[0][0]
    return redirect("/productdescription/"+str(pid))


def home(request):
    global cart_quantity

    query_quantity = "select count(*) from cart where UserID = '{}';".format(username)
    cursor.execute(query_quantity)
    cart_quantity = (tuple(cursor.fetchall()))[0][0]

    query = "SELECT * FROM PRODUCT NATURAL JOIN CATEGORY ORDER BY PRODUCTID DESC LIMIT 4;"
    cursor.execute(query)
    products = tuple(cursor.fetchall())

    query_category = "SELECT * FROM Category;"
    cursor.execute(query_category)
    categories = tuple(cursor.fetchall())

    categoryList = {}

    for category in categories:
        query_products = "SELECT * FROM Product where CategoryID = {};".format(category[0])
        cursor.execute(query_products)
        productsList = tuple(cursor.fetchall())
        categoryList[category[1]] = productsList

    return render(request, 'main.html', {'cart_items_num': cart_quantity, 'products': products, 'categoryList': categoryList.items(), 'uid': username})

def cart(request):
    global cart_quantity

    query = "select A.ProductID, ProductName, A.Quantity, Price, A.Quantity*Price, A.SellerID from (select * from Product NATURAL JOIN cart) A, seller_product S where A.ProductID = S.ProductID and A.SellerID = S.SellerID and UserID = '{}';".format(username)
    cursor.execute(query)
    cart_items = tuple(cursor.fetchall())

    total_query = "select sum(A.Quantity*Price) from (select * from Product NATURAL JOIN cart) A, seller_product S where A.ProductID = S.ProductID and A.SellerID = S.SellerID and UserID = '{}';".format(username)
    cursor.execute(total_query)
    total = (tuple(cursor.fetchall()))[0][0]

    return render(request, 'cart.html', {'cart_items_num': cart_quantity, 'cart_items': cart_items, 'total': total, 'uid': username})


def confirmation(request):
    global cart_quantity

    order_query = "select OrderID from order_quantity where UserID = '{}' order by OrderID desc LIMIT 1;".format(username)
    cursor.execute(order_query)
    order_id = (tuple(cursor.fetchall()))[0][0]

    query = "select OrderID, A.ProductID, ProductName, A.Quantity, Price, A.Quantity*Price, A.SellerID, DatePlaced from (select * from Product NATURAL JOIN order_quantity) A, seller_product S where A.ProductID = S.ProductID and A.SellerID = S.SellerID and OrderID = '{}';".format(order_id)
    cursor.execute(query)
    order_items = tuple(cursor.fetchall())

    total_query = "select sum(A.Quantity*Price) from (select * from Product NATURAL JOIN order_quantity) A, seller_product S where A.ProductID = S.ProductID and A.SellerID = S.SellerID and OrderID = '{}';".format(order_id)
    cursor.execute(total_query)
    total = (tuple(cursor.fetchall()))[0][0]

    address_query = "SELECT * FROM (USER natural join PIN), USER_CONTACT WHERE USER.USERID = USER_CONTACT.USERID AND USER.USERID = '{}'".format(username)
    cursor.execute(address_query)
    user_detail = tuple(cursor.fetchall())

    return render(request, 'confirmation.html', {'cart_items_num': cart_quantity, 'order_items': order_items, 'total': total, 'uid': username, 'user_detail': user_detail[0], 'order_id': order_id})

def productdescription(request, pid):
    global cart_quantity
    global username
    query = "SELECT * FROM PRODUCT WHERE ProductID = '{}'".format(pid)
    cursor.execute(query)
    product = tuple(cursor.fetchall())
    name = product[0][1]
    price = product[0][4]
    description = product[0][3]
    rating = product[0][2]

    query_seller = "Select seller_product.SellerID, SellerName, Quantity, Price from seller_product, seller where seller_product.SellerID = seller.SellerID and ProductID = {};".format(pid)
    cursor.execute(query_seller)
    sellers = tuple(cursor.fetchall())

    query_cat = "SELECT CategoryName FROM CATEGORY WHERE CategoryID = '{}'".format(product[0][5])
    cursor.execute(query_cat)
    category = tuple(cursor.fetchall())[0][0]
    return render(request, 'productdescription.html', {'cart_items_num': cart_quantity, 'name': name, 'price': price, 'category': category, 'description': description, 'sellers': sellers, 'rating': rating, 'uid': username, 'pid': pid})

def search(request):
    return render(request, 'search.html', {'cart_items_num': cart_quantity, 'uid': username})

def user(request, uid):
    global cart_quantity
    query = "SELECT * FROM (USER natural join PIN), USER_CONTACT WHERE USER.USERID = USER_CONTACT.USERID AND USER.USERID = '{}'".format(uid)
    cursor.execute(query)
    user = tuple(cursor.fetchall())

    query_past = "SELECT A.ORDERID, PRODUCTNAME, Quantity, PRICE FROM ((SELECT orderid, PRODUCTNAME, O.Quantity, O.Quantity*PRICE as PRICE FROM order_quantity O, seller_product S, PRODUCT P WHERE P.ProductID = S.ProductID AND  O.ProductID = S.ProductID AND O.SellerID = S.SellerID AND UserID = '{}') as A left outer join (select * from order_date) as B on A.orderid = b.orderid) where DateDelivered is NOT NULL;".format(uid)
    cursor.execute(query_past)
    past_order = tuple(cursor.fetchall())

    query_present = "SELECT A.ORDERID, PRODUCTNAME, Quantity, PRICE FROM ((SELECT orderid, PRODUCTNAME, O.Quantity, O.Quantity*PRICE as PRICE FROM order_quantity O, seller_product S, PRODUCT P WHERE P.ProductID = S.ProductID AND  O.ProductID = S.ProductID AND O.SellerID = S.SellerID AND UserID = '{}') as A left outer join (select * from order_date) as B on A.orderid = b.orderid) where DateDelivered is NULL;".format(uid)
    cursor.execute(query_present)
    present_order = tuple(cursor.fetchall())

    return render(request, 'user.html', {'cart_items_num': cart_quantity, 'user': user[0], 'past_order': past_order, 'present_order': present_order})

def seller(request, sid):
    global cart_quantity
    query = "SELECT * FROM (SELLER natural join PIN natural join GSTIN), SELLER_CONTACT WHERE SELLER.SELLERID = SELLER_CONTACT.SELLERID AND SELLER.SELLERID = '{}'".format(sid)
    cursor.execute(query)
    seller = tuple(cursor.fetchall())

    order_query = "SELECT PRODUCTNAME, B.QUANTITY, B.QUANTITY*PRICE FROM (SELECT * FROM SELLER_PRODUCT NATURAL JOIN SELLER NATURAL JOIN PRODUCT) AS A, (SELECT * FROM order_date NATURAL JOIN order_quantity) AS B WHERE A.SELLERID = B.SELLERID AND A.PRODUCTID = B.PRODUCTID AND A.SELLERID = '{}';".format(sid)
    cursor.execute(order_query)
    order_delivered = tuple(cursor.fetchall())

    total_query = "SELECT sum(B.QUANTITY*PRICE) FROM (SELECT * FROM SELLER_PRODUCT NATURAL JOIN SELLER NATURAL JOIN PRODUCT) AS A, (SELECT * FROM order_date NATURAL JOIN order_quantity) AS B WHERE A.SELLERID = B.SELLERID AND A.PRODUCTID = B.PRODUCTID AND A.SELLERID = '{}';".format(sid)
    cursor.execute(total_query)
    total = cursor.fetchall()[0]

    product_query = "SELECT ProductID, ProductName FROM PRODUCT where productID not in (select productid from seller_product where SellerID = '{}');".format(sid)
    cursor.execute(product_query)
    product_list = tuple(cursor.fetchall())

    existing_product_query = "SELECT ProductID, ProductName FROM PRODUCT where productID in (select productid from seller_product where SellerID = '{}');".format(sid)
    cursor.execute(existing_product_query)
    existing_product = tuple(cursor.fetchall())

    return render(request, 'seller.html', {'cart_items_num': cart_quantity, 'seller': seller[0], 'order_delivered': order_delivered, 'total': total[0], 'sid': sid, 'product_list': product_list, 'existing_product': existing_product})

def addProduct(request, sid):

    productID = ""
    price = ""
    quantity = ""

    if request.method=="POST":
        data=request.POST
        for key,value in data.items():
            if key == "products":
                productID = value
            if key == "quantity":
                quantity = value
            if key == "price":
                price = value

        query = "INSERT INTO SELLER_PRODUCT VALUES('{}', '{}', '{}', '{}')".format(productID, sid, price, quantity)   
        cursor.execute(query)
        connection.commit()

    return redirect("/seller/" + sid)

def updateQuantity(request, sid):

    productID = ""
    quantity = ""

    if request.method=="POST":
        data=request.POST
        for key,value in data.items():
            if key == "products":
                productID = value
            if key == "quantity":
                quantity = value

        query = "update seller_product set quantity = {} where sellerid='{}' and productid={};".format(quantity, sid, productID)   
        cursor.execute(query)
        connection.commit()

    return redirect("/seller/" + sid)

def placeOrder(request):
    global cart_quantity

    order_query = "select OrderID from order_quantity order by OrderID desc LIMIT 1;"
    cursor.execute(order_query)
    order_id = tuple(cursor.fetchall())[0][0]

    query = "select * from cart where UserID = '{}';".format(username)
    cursor.execute(query)
    cart_items = tuple(cursor.fetchall())

    for item in cart_items:
        insert_query = "INSERT INTO ORDER_QUANTITY VALUES({}, {}, '{}', '{}', {}, '{}')".format(int(order_id) + 1, item[2], item[1], item[0], item[3], date.today())
        cursor.execute(insert_query)
        connection.commit()

        delete_query = "DELETE FROM CART WHERE UserID = '{}' and SellerID = '{}';".format(username, item[1])
        cursor.execute(delete_query)
        connection.commit()

    query_quantity = "select count(*) from cart where UserID = '{}';".format(username)
    cursor.execute(query_quantity)
    cart_quantity = (tuple(cursor.fetchall()))[0][0]

    return redirect('/confirmation')

def logoutUser(request):
    global username 
    username = ""
    return redirect("/")
