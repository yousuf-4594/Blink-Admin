from django.shortcuts import render, redirect, HttpResponse
import firebase_admin
from firebase_admin import credentials, firestore, auth
from .forms import RestaurantForm, CustomerForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django import forms
from django.http import JsonResponse
from typing import List, Dict, Tuple

# cred = credentials.Certificate("blink-a34ae-firebase-adminsdk-5myau-fd79745951.json")
# firebase_admin.initialize_app(cred, {"databaseURL": "https://blink-a34ae.firebaseio.com"})
if not firebase_admin._apps:
    try:
        cred = credentials.Certificate("/home/blinkadmin/Blink-Admin/blinkadmin/blink-a34ae-firebase-adminsdk-5myau-fd79745951.json")
        firebase_admin.initialize_app(cred, {"databaseURL": "https://blink-a34ae.firebaseio.com"})
    except Exception as e:
        print(e)

# with open('/home/blinkadmin/Blink-Admin/blinkadmin/base/conn_status.txt', 'r') as file:
#     word = file.readline().strip()
#     if word == "false":
#         initialize_firebase()
#         with open('/home/blinkadmin/Blink-Admin/blinkadmin/base/conn_status.txt', 'w') as file:
#             word = "true"
#             file.write(word)

db = firestore.client()

class Customer:
    def __init__(self, uid, firstName, lastName):
        self.uid = uid
        self.firstName = firstName
        self.lastName = lastName


class Restaurant:
    def __init__(self, id, name, owner, views):
        self.id = id
        self.name = name
        self.owner = owner
        self.views = views


class Product:
    def __init__(self, name, customer, restaurant, price):
        self.name = name
        self.customer = customer
        self.restaurant = restaurant
        self.price = price


class Order:
    def __init__(self, id, price, customerId, customerName, restaurantName, status, placedAt):
        self.id = id
        self.products = []
        self.price = price
        self.customerId = customerId
        self.customerName = customerName
        self.restaurantName = restaurantName
        self.status = status
        self.placedAt = placedAt
    
def getRestaurantNames() -> List[str]:
    """
    This function returns all names of restaurants

    Parameters:
    None

    Returns:
    - List[str]: List of restaurants
    """
    names = []
    collectionRef = db.collection("restaurants")
    docRef = collectionRef.stream()
    for doc in docRef:
        restaurant = doc.to_dict()
        names.append((doc.id, restaurant["name"]))
    return names

class FoodForm(forms.Form):
    name = forms.CharField(label="Item Name")
    restaurant = forms.ChoiceField(choices=getRestaurantNames())
    category = forms.CharField(label="Category")
    price = forms.DecimalField()



def getOrders() -> List[Order]:
    """
    This function returns all orders

    Parameters:
    None

    Returns:
    - List[Order]: List of Orders
    """
    orders = []
    ref = db.collection("orders")
    docs = ref.stream()
    for order in docs:
        ord = order.to_dict()
        o = Order(id=order.id, price=int(ord["price"]), customerId=ord["customerid"], customerName=getCustomerName(
            ord["customerid"]), restaurantName=ord["restaurant"]["name"], status=ord["status"], placedAt=ord["placedat"])
        orders.append(o)
    return orders  


def getTrendingRestaurants() -> List[List]:
    """
    This function top 3 trending restaurants based on views

    Parameters:
    None

    Returns:
    - List[List[str, int]]: List of restaurants that contains lists of 2 elements in the form [restaurant_name, views]
    """
    restaurantsRef = db.collection("restaurants").stream()
    restaurants = []
    for restaurant in restaurantsRef:
        res = restaurant.to_dict()
        restaurants.append([res["name"], int(res["views"])])
    restaurants.sort(key=lambda x: x[1], reverse=True)
    return restaurants[:3]


def getCustomerName(id: str) -> str:
    """
    This returns full name of a given customer

    Parameters:
    - str: id of customer

    Returns:
    - str: full name of customer
    """
    collectionRef = db.collection("customers").document(id)
    docRef = collectionRef.get()
    customer = docRef.to_dict()
    return f"{customer['firstname']} {customer['lastname']}"


def getRestaurants() -> List[Restaurant]:
    """
    This function returns restaurants

    Parameters:
    None

    Returns:
    - List[Restaurant]: List of restaurants
    """
    restaurants = []
    try:
        ref = db.collection("restaurants")
        docs = ref.stream()
        for restaurant in docs:
            res = restaurant.to_dict()
            restaurants.append(Restaurant(
                restaurant.id, res["name"], res["ownername"], res["views"]))
    except Exception as e:
        print(e)
    return restaurants


def getTotalEarnings(orders: List[Order]) -> int:
    """
    This function returns total revenue of all restaurants combined

    Parameters:
    - List[Order]: List of Orders

    Returns:
    - int: Total earnings
    """
    total = 0
    for order in orders:
        total += int(order.price)

    return total


def getTotalViews(restaurants: List[Restaurant]) -> int:
    """
    This function returns total views of all restaurants combined

    Parameters:
    - List[Restaurant]: List of Restaurants

    Returns:
    - int: Total views
    """
    total = 0
    for restaurant in restaurants:
        total += int(restaurant.views)

    return total


def addNewRestaurant(data):
    """
    This function adds new restaurant

    Parameters:
    - Dict[str, Any]: Restaurant's data

    Returns:
    None
    """
    restaurant = {
        "name": data["name"],
        "email": data["email"],
        "ownername": data["ownername"],
        "username": data["username"],
        "description": data["description"],
        "Estimated Time": 0,
        "Review": {
            "Rating Count": 0,
            "Stars": 0
        },
        "views": 0
    }

    collectionRef = db.collection("restaurants")
    updateTime, ref = collectionRef.add(restaurant)


def getRestaurant(id: str):
    """
    This function returns restaurant's data

    Parameters:
    - str: Restaurant's ID

    Returns:
    - Dict[str, Any]: Restaurant's data
    """
    docRef = db.collection('restaurants').document(id)
    restaurantRef = docRef.get()
    restaurant = restaurantRef.to_dict()
    d = {"name": restaurant["name"], "email": restaurant["email"], "ownername": restaurant["ownername"],
         "description": restaurant["description"], "username": restaurant["username"]}
    return d


def updateRestaurant(id: str, restaurant):
    """
    This function updates Restaurant's information

    Parameters:
    - str: Restaurant's ID
    - Dict[str, Any]: Restaurant's information

    Returns:
    - int: Total earnings
    """
    docRef = db.collection("restaurants").document(id)
    newData = {
        "name": restaurant["name"],
        "email": restaurant["email"],
        "ownername": restaurant["ownername"],
        "description": restaurant["description"],
        "username": restaurant["username"]
    }
    docRef.update(newData)

def getAllCustomers() -> List[Customer]:
    """
    This function returns all customers

    Parameters:
    None

    Returns:
    - List[Customer]: List of Customers
    """
    customers = []
    for user in auth.list_users().iterate_all():
        collectionRef = db.collection("customers").document(user.uid)
        documentRef = collectionRef.get()
        cust = documentRef.to_dict()
        customer = Customer(documentRef.id, cust["firstname"], cust["lastname"])
        customers.append(customer)
    return customers

def addNewCustomer(data):
    """
    This function adds new Customer

    Parameters:
    - Dict[str, Any]: Customer's data

    Returns:
    None
    """
    try:
        user = None
        user = auth.create_user(email=data["email"], password=data["password"])
        if user is not None:
            docRef = db.collection("customers").document(user.uid)
            docRef.set({"firstname": data["firstname"], "lastname": data["lastname"]})
    except Exception as e:
        print(e)

def getCustomer(id: str):
    """
    This function returns Customer's data

    Parameters:
    - str: Customer's ID

    Returns:
    - Dict[str, Any]: Customer's Data
    """
    collectionRef = db.collection("customers").document(id)
    documentRef = collectionRef.get()
    doc = documentRef.to_dict()
    firstname = doc["firstname"]
    lastname = doc["lastname"]
    customer = {
        "firstname": firstname,
        "lastname": lastname,
        "email": "",
        "password": ""
    }
    return customer

def updateCustomer(id, data):
    try:
        auth.update_user(
            id,
            email=data["email"],
            password=data["password"],
        )
        docRef = db.collection("customers").document(id)
        newData = {
            "firstname": data["firstname"],
            "lastname": data["lastname"]
        }
        docRef.update(newData)
    except Exception as e:
        print(e)

def addNewFood(data):
    restaurantRef = db.collection("restaurants").document(data["restaurant"])
    foodsRef = restaurantRef.collection("foodItems")
    food = {
        "Category Name": data["category"],
        "Like Count": 0,
        "Price": int(data["price"]),
        "Prod Name": data["name"]
    }
    foodsRef.add(food)

# Create your views here.


@login_required(login_url='login-page')
def homePage(request):
    orders = getOrders()
    pendingOrders = getPendingOrders()
    earnings = getTotalEarnings(orders)
    trendingRestaurants = getTrendingRestaurants()
    context = {"orders": orders, "earnings": earnings, "trendingRestaurants": trendingRestaurants, "pendingOrders": pendingOrders}
    return render(request, 'base/index.html', context)


def loginPage(request):
    if request.user.is_authenticated:
        return redirect('home-page')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home-page')
    context = {}
    return render(request, 'base/login.html', context)


def logoutUser(request):
    logout(request)
    return redirect('login-page')


@login_required(login_url='login-page')
def ordersPage(request):
    orders = getOrders()
    context = {"orders": orders}
    return render(request, 'base/orders.html', context)


@login_required(login_url='login-page')
def customersPage(request):
    customers = getAllCustomers()
    context = {"customers": customers}
    return render(request, "base/customers.html", context)


@login_required(login_url='login-page')
def restaurantsPage(request):
    restaurants = getRestaurants()
    context = {"restaurants": restaurants}
    return render(request, 'base/restaurants.html', context)


@login_required(login_url='login-page')
def analyticsPage(request):
    context = {}
    return HttpResponse("Analytics")


@login_required(login_url='login-page')
def newRestaurantPage(request):
    if request.method == 'POST':
        form = RestaurantForm(request.POST)

        if form.is_valid():
            addNewRestaurant(form.cleaned_data)
            return redirect('restaurants-page')
    else:
        form = RestaurantForm()

    context = {"form": form}
    return render(request, 'base/new_restaurant_form.html', context)


@login_required(login_url='login-page')
def deleteRestaurantPage(request, id):
    docRef = db.collection('restaurants').document(id)
    docRef.delete()
    return redirect('restaurants-page')


@login_required(login_url='login-page')
def editRestaurantPage(request, id):
    restaurant = getRestaurant(id)
    if request.method == 'POST':
        form = RestaurantForm(request.POST)
        if form.is_valid():
            updateRestaurant(id, form.cleaned_data)
        return redirect('restaurants-page')
    else:
        form = RestaurantForm(initial=restaurant)

    context = {"form": form, "id": id}
    return render(request, 'base/edit_restaurant_form.html', context)

@login_required(login_url='login-page')
def newCustomerPage(request):
    if request.method == 'POST':
        form = CustomerForm(request.POST)
        if form.is_valid():
            addNewCustomer(form.cleaned_data)
        return redirect('customers-page')
    else:
        form = CustomerForm()

    context = {"form": form}
    return render(request, 'base/new_customer_form.html', context)

@login_required(login_url='login-page')
def deleteCustomerPage(request, id):
    try:
        auth.delete_user(id)
        docRef = db.collection('customers').document(id)
        docRef.delete()
    except Exception as e:
        print(e)

    return redirect('customers-page')

@login_required(login_url='login-page')
def editCustomerPage(request, id):
    customer = getCustomer(id)
    if request.method == 'POST':
        form = CustomerForm(request.POST)
        if form.is_valid():
            updateCustomer(id, form.cleaned_data)
        return redirect('customers-page')
    else:
        form = CustomerForm(initial=customer)

    context = {"form": form, "id": id}
    return render(request, 'base/edit_customer_form.html', context)

@login_required(login_url='login-page')
def foodItemsPage(request):
    foods = []
    collectionRef = db.collection('restaurants')
    restaurants = collectionRef.stream()
    
    for restaurant in restaurants:
        restaurantId = restaurant.id
        foodItems = db.collection("restaurants").document(restaurantId).collection("foodItems").stream()
        for docs in foodItems:
            foodId = docs.id
            data = docs.to_dict()
            food = {
                "id": foodId,
                "restaurantId": restaurantId,
                "restaurantName": restaurant.to_dict()["name"],
                "name": data["Prod Name"],
                "price": data["Price"],
                "category": data["Category Name"],
                "url": f"{restaurantId}:{foodId}"
            }
            foods.append(food)

    context = {"foods": foods}
    return render(request, 'base/food-items.html', context)


@login_required(login_url='login-page')
def newFoodPage(request):
    if request.method == 'POST':
        form = FoodForm(request.POST)

        if form.is_valid():
            addNewFood(form.cleaned_data)
            return redirect('fooditems-page')
    else:
        form = FoodForm()

    context = {"form": form}
    return render(request, 'base/new_food_form.html', context)

@login_required(login_url='login-page')
def deleteFoodPage(request, id):
    ids = id.split(':')
    restaurantRef = db.collection("restaurants").document(ids[0])
    foodRef = restaurantRef.collection("foodItems").document(ids[1])
    foodRef.delete()
    return redirect("fooditems-page")

@login_required(login_url='login-page')
def fetchViews(request):
    totalViews = getTotalViews(getRestaurants())
    return JsonResponse({"views": totalViews})


def getPendingOrders():
    orders = []
    ref = db.collection("orders")
    docs = ref.stream()
    for order in docs:
        ord = order.to_dict()
        if ord["status"] == "pending":
            o = Order(id=order.id, price=int(ord["price"]), customerId=ord["customerid"], customerName=getCustomerName(
                ord["customerid"]), restaurantName=ord["restaurant"]["name"], status=ord["status"], placedAt=ord["placedat"])
            orders.append(o)
    return orders  