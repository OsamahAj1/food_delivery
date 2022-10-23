from django.shortcuts import render

import json
from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.urls import reverse
from django.core.exceptions import ObjectDoesNotExist
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required

from client_app.models import User, Cart
from deliveryperson_app.models import Order
from restaurant_app.models import Food


@login_required(login_url='/restaurants/login')
def index(request):

    # check if user is client
    if request.user.is_client is True:
        return HttpResponseRedirect(reverse("client_app:index"))

    # check if user is deliveryperson
    if request.user.is_deliveryperson is True:
        return HttpResponseRedirect(reverse("deliveryperson_app:index"))

    return render(request, "restaurant_app/index.html",{
        "orders": Order.objects.filter(restaurant=request.user, is_active=True, is_sent=True)
    })


@login_required(login_url='/')
def add_food(request):

    # if request is post add food
    if request.method == "POST":

        # make sure user is resaurant
        if request.user.is_restaurant is False:
            return render(request, "restaurant_app/error.html", {
                "error": "U must be restaurant to access this page"
            })

        # get inputs from user
        food = request.POST.get("food", "")
        image = request.POST.get("image", "")
        des = request.POST.get("des", "")
        price = request.POST.get("price", "")

        # errors checking
        if not food or not price or not des or not image:
            return render(request, "restaurant_app/add_food.html", {
                "message": "Must fill all fields",
                "food": food,
                "image": image,
                "des": des,
                "price": price
            })

        if len(image) > 200:
            return render(request, "restaurant_app/add_food.html", {
                "message": "image url is too long",
                "food": food,
                "image": image,
                "des": des,
                "price": price
            })

        try:
            price = round(float(price), 2)
        except ValueError:
            return render(request, "restaurant_app/add_food.html", {
                "message": "Price must be postive digit",
                "food": food,
                "image": image,
                "des": des,
                "price": price
            })

        # add data to db
        new_food = Food(food=food, image=image, price=price, des=des, restaurant=request.user)
        new_food.save()

        # redirect to index
        return HttpResponseRedirect(reverse("restaurant_app:index"))

    # if request is get show add food page
    else:
        # make sure user is resaurant
        if request.user.is_restaurant is False:
            return render(request, "restaurant_app/error.html", {
                "error": "U must be restaurant to access this page"
            })

        return render(request, "restaurant_app/add_food.html")


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:

            # check if user is restaurant
            if user.is_restaurant is False:
                return render(request, "restaurant_app/error.html", {
                    "error": "U must be restaurant to login"
                })

            login(request, user)
            return HttpResponseRedirect(reverse("restaurant_app:index"))
        else:
            return render(request, "restaurant_app/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "restaurant_app/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("client_app:index"))


def register(request):
    if request.method == "POST":

        # get inputs from user
        username = request.POST["username"]
        email = request.POST["email"]
        des = request.POST["des"]
        address = request.POST["address"]
        image = request.POST.get("image", False)

        # errors cheking
        if not username or not email or not des or not image or not address:
            return render(request, "restaurant_app/register.html", {
                "message": "Must fill all fields"
            })


        if len(image) > 200:
            return render(request, "restaurant_app/register.html", {
                "message": "Image url is too long"
            })

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "restaurant_app/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.is_restaurant = True
            user.image = image
            user.des = des
            user.address = address
            user.save()
        except IntegrityError:
            return render(request, "restaurant_app/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("restaurant_app:index"))
    else:
        return render(request, "restaurant_app/register.html")
