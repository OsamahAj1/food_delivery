import json
from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.urls import reverse
from django.core.exceptions import ObjectDoesNotExist
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required

from client_app.models import User, Cart, Old_orders
from client_app.views import restaurant
from deliveryperson_app.models import Order
from restaurant_app.models import Food


@login_required(login_url='/delivery_person/login')
def index(request):

    # check if user is client
    if request.user.is_client is True:
        return HttpResponseRedirect(reverse("client_app:index"))

    # check if user is restaurant
    if request.user.is_restaurant is True:
        return HttpResponseRedirect(reverse("restaurant_app:index"))

    return render(request, "deliveryperson_app/index.html", {
        "orders": Order.objects.filter(is_active=False)
    })


@login_required(login_url='/delivery_person/login')
def live_order(request):

    # check if user is delivery person
    if request.user.is_deliveryperson is False:
        return render(request, "deliveryperson_app/error.html", {
            "error": "you must be delivery person to access this page"
        })

    # get order
    try:
        order = Order.objects.filter(deliveryperson=request.user).first()
    except ObjectDoesNotExist:
        # if there is no order assign order to none
        order = None

    # render page with data
    return render(request, "deliveryperson_app/order.html", {
        "order": order
    })


@login_required(login_url='/delivery_person/login')
def delivered(request):

    # make sure request method post
    if request.method != "POST":
        return render(request, "deliveryperson_app/error.html", {
            "error": "Request Error"
        })

    # check if user is delivery person
    if request.user.is_deliveryperson is False:
        return render(request, "deliveryperson_app/error.html", {
            "error": "U must be delivery person to access this route"
        })

    # check if there is order
    try:
        order = Order.objects.get(deliveryperson=request.user)
    except ObjectDoesNotExist:
        return render(request, "deliveryperson_app/error.html", {
            "error": "Order error"
        })

    # move order to old orders
    old_order = Old_orders(restaurant=order.restaurant, deliveryperson=order.deliveryperson, user=order.user, order=order.order, sum_order=order.sum_order)
    old_order.save()

    # delete the order
    order.delete()

    # redirect to index
    return HttpResponseRedirect(reverse("deliveryperson_app:index"))


@login_required(login_url='/delivery_person/login')
def old_orders(request):

    # check if user is deliveryperson
    if request.user.is_deliveryperson is False:
        return render(request, "deliveryperson_app/error.html", {
            "error": "you must be delivery person to access this page"
        })

    # get old orders
    old_orders = Old_orders.objects.filter(deliveryperson=request.user)

    # render template with data
    return render(request, "deliveryperson_app/old_orders.html", {
        "old_orders": old_orders,
    })


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:

            # check if user is restaurant
            if user.is_deliveryperson is False:
                return render(request, "deliveryperson_app/error.html", {
                    "error": "U must be deliveryperson to login"
                })

            login(request, user)
            return HttpResponseRedirect(reverse("deliveryperson_app:index"))
        else:
            return render(request, "deliveryperson_app/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "deliveryperson_app/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("client_app:index"))


def register(request):
    if request.method == "POST":

        # get inputs from user
        username = request.POST["username"]
        email = request.POST["email"]
        car = request.POST["car"]
        image = request.POST.get("image", False)
        number = request.POST["number"]

        # errors cheking
        if not username or not email or not car or not image or not number:
            return render(request, "deliveryperson_app/register.html", {
                "message": "Must fill all fields"
            })


        if len(image) > 200:
            return render(request, "deliveryperson_app/register.html", {
                "message": "Image url is too long"
            })

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "deliveryperson_app/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.is_deliveryperson = True
            user.image = image
            user.car = car
            user.number = number
            user.save()
        except IntegrityError:
            return render(request, "deliveryperson_app/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("deliveryperson_app:index"))
    else:
        return render(request, "deliveryperson_app/register.html")
