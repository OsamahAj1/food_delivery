import json
from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.urls import reverse
from django.core.exceptions import ObjectDoesNotExist
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from django.template.defaulttags import register
from django.db.models import Sum

from client_app.models import Old_orders, User, Cart
from deliveryperson_app.models import Order
from restaurant_app.models import Food


@register.filter
def usd(value):
    """Format value as USD."""
    return f"${value:,.2f}"


def index(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect(reverse("client_app:home"))
    return render(request, "client_app/index.html")


@login_required(login_url='/login')
def home(request):

    # check if user is restaurant
    if request.user.is_restaurant is True:
        return HttpResponseRedirect(reverse("restaurant_app:index"))

    # check if user is deliveryperson
    if request.user.is_deliveryperson is True:
        return HttpResponseRedirect(reverse("deliveryperson_app:index"))

    # get all restaurants
    restaurantss = User.objects.filter(is_restaurant=True, is_superuser=False)
    paginator = Paginator(restaurantss, 12)
    page_number = request.GET.get('page')
    restaurants = paginator.get_page(page_number)

    return render(request, "client_app/home.html", {
        "restaurants": restaurants,
    })


@login_required(login_url='/login')
def restaurant(request, res):

    # check if user is client
    if request.user.is_client is False:
        return render(request, "client_app/error.html", {
            "error": "U must be client to access this page"
        })

    # check if restaurant exist
    try:
        restaurant = User.objects.get(username=res)
    except ObjectDoesNotExist:
        return render(request, "client_app/error.html", {
            "error": "restaurant doesn't exist"
        })

    # check if it's restaurant
    if restaurant.is_restaurant is False:
        return render(request, "client_app/error.html", {
            "error": "restaurant doesn't exist"
        })

    # get food
    food = Food.objects.filter(restaurant=restaurant)

    # render page with data
    return render(request, "client_app/restaurant_page.html", {
        "food": food,
        "restaurant": restaurant,
    })


@login_required(login_url='/login')
def cart(request):

    # check if user is client
    if request.user.is_client is False:
        return JsonResponse({"error": "You must be user to see cart items"}, status=400)

    # get user cart
    cart = Cart.objects.filter(user=request.user)

    # get sum cart price
    sum_price_cart = cart.aggregate(Sum('sum_price'))['sum_price__sum']

    # render cart page with data
    return render(request, "client_app/cart.html", {
        "cart": cart,
        "sum_price_cart": sum_price_cart,
    })


@login_required(login_url='/login')
def sum_cart(request):

    # check if user is client
    if request.user.is_client is False:
        return JsonResponse({"error": "You must be user see cart sum"}, status=400)

    # get sum of cart
    sum_cart = Cart.objects.filter(user=request.user).aggregate(Sum('n'))['n__sum']

    # if it's empty return 0
    if not sum_cart:
        sum_cart = 0

    # return sum_cart
    return JsonResponse({"sum": sum_cart}, status=201)


@login_required(login_url='/login')
def add_cart(request, food_id):

    # make sure request method post
    if request.method != "POST":
        return JsonResponse({"error": "POST request required."}, status=400)

    # check if user is client
    if request.user.is_client is False:
        return JsonResponse({"error": "You must be user to add items to cart"}, status=400)

    # check if there's n
    data = json.loads(request.body)
    nn = [n.strip() for n in data.get("n").split(",")]

    # if it's empty return error
    if nn == [""]:
        return JsonResponse({"error": "Must Provide Post n"}, status=400)

    # get n
    n = data.get("n", "")

    # make sure n and food_id is number
    if str(n).isdigit() is False or str(food_id).isdigit() is False:
        return JsonResponse({"error": f"Error1"}, status=400)
    
    n = int(n)
    food_id = int(food_id)

    # make sure n and food_id is not 0
    if n == 0 or food_id == 0:
        return JsonResponse({"error": "Error2"}, status=400)

    # make sure food exist
    try:
        food = Food.objects.get(pk=food_id)
    except ObjectDoesNotExist:
        return JsonResponse({"error": "food doesn't exist"}, status=400)

    # get user cart
    cart = Cart.objects.filter(user=request.user)

    # calculate sum
    sum_price = round(food.price * n, 2)

    # if item already in cart update n and sum
    try:
        in_cart = Cart.objects.get(user=request.user, item=food)
        in_cart.n = in_cart.n + n
        in_cart.sum_price = in_cart.sum_price + sum_price
        in_cart.save()
        return JsonResponse({"success": "Added successfully"}, status=201)
    except ObjectDoesNotExist:
        pass

    # if cart is empty add item to it
    if not cart:

        # add item to db
        item = Cart(user=request.user, item=food, n=n, sum_price=sum_price)
        item.save()

        # return success
        return JsonResponse({"success": "Added successfully"}, status=201)
    
    # if cart is not empty check if the item from the same restaurant
    else:

        # check
        if cart.first().item.restaurant.id != food.restaurant.id:
            return JsonResponse({"error": "All items in cart must be from the same restaurant."}, status=400)

        # add item to db
        item = Cart(user=request.user, item=food, n=n, sum_price=sum_price)
        item.save()

        # return success
        return JsonResponse({"success": "Added successfully"}, status=201)


@login_required(login_url='/login')
def update_cart(request, cart_id):

    # make sure request method post
    if request.method != "POST":
        return JsonResponse({"error": "POST request required."}, status=400)
    
    # check if user is client
    if request.user.is_client is False:
        return JsonResponse({"error": "You must be user to update items in cart"}, status=400)

    # check if there's n
    data = json.loads(request.body)
    nn = [n.strip() for n in data.get("n").split(",")]

    # if it's empty return error
    if nn == [""]:
        return JsonResponse({"error": "Must Provide Post n"}, status=400)

    # get n
    n = data.get("n", "")

    # make sure n and cart_id is number
    if str(n).isdigit() is False or str(cart_id).isdigit() is False:
        return JsonResponse({"error": f"Error1"}, status=400)

    n = int(n)
    cart_id = int(cart_id)

    # make sure n and cart_id is not 0
    if n == 0 or cart_id == 0:
        return JsonResponse({"error": "Error2"}, status=400)

    # make sure cart item exist
    try:
        cart_item = Cart.objects.get(pk=cart_id)
    except ObjectDoesNotExist:
        return JsonResponse({"error": "food is not in cart"}, status=400)

    # calculate sum
    sum_price = round(cart_item.item.price * n, 2)

    # update db
    cart_item.n = n
    cart_item.sum_price = sum_price
    cart_item.save()

    # get sum of cart
    sum_cart = Cart.objects.filter(user=request.user).aggregate(Sum('sum_price'))['sum_price__sum']

    # return success
    return JsonResponse({"success": "Updated successfully", "sum_cart": sum_cart, "sum_price": usd(cart_item.sum_price)}, status=201)


@login_required(login_url='/login')
def remove_cart(request, cart_id):

    # make sure request method post
    if request.method != "POST":
        return JsonResponse({"error": "POST request required."}, status=400)

    # check if user is client
    if request.user.is_client is False:
        return JsonResponse({"error": "You must be user to delete items from cart"}, status=400)

    # make cart_id is number
    if str(cart_id).isdigit() is False:
        return JsonResponse({"error": f"Error1"}, status=400)

    cart_id = int(cart_id)

    # cart_id is not 0
    if cart_id == 0:
        return JsonResponse({"error": "Error2"}, status=400)

    # make sure cart item exist
    try:
        cart_item = Cart.objects.get(pk=cart_id)
    except ObjectDoesNotExist:
        return JsonResponse({"error": "food is not in cart"}, status=400)

    # delete from db
    cart_item.delete()

    # get sum of cart
    sum_cart = Cart.objects.filter(user=request.user).aggregate(Sum('n'))['n__sum']

    # if cart is empty return 0
    if not sum_cart:
        sum_cart = 0

    # return success
    return JsonResponse({"success": "Removed successfully", "sum_cart": sum_cart}, status=201)


@login_required(login_url='/login')
def place_order(request):

    # make sure request method post
    if request.method != "POST":
        return render(request, "client_app/error.html", {
            "error": "Request Error"
        })
    
    # check if user is client
    if request.user.is_client is False:
        return render(request, "client_app/error.html", {
            "error": "U must be client to access this page"
        })

    # check if there is already order
    try:
        Order.objects.get(user=request.user)
        return render(request, "client_app/error.html", {
            "error": "there is already order in pending please wait for order to end or cancel order if possible"
        })
    except ObjectDoesNotExist:
        pass

    # get user cart
    cart = Cart.objects.filter(user=request.user)

    # check if cart is empty
    if not cart:
        return render(request, "client_app/error.html", {
            "error": "Cart is empty"
        })

    # get cart items and numbers
    items = cart.only("item", "n")

    # create list for order
    order = []

    # loop through items and add the order to single list
    for i in items:
        order.append(f"{i.n} {i.item.food}")
    
    # make the list single big string with white space at the end
    order = " - ".join(order)

    # get restaurant
    restaurant = items.first().item.restaurant

    # get sum price cart
    sum_price_cart = cart.aggregate(Sum('sum_price'))['sum_price__sum']

    # save order to db
    new_order = Order(restaurant=restaurant, user=request.user, order=order, sum_order=sum_price_cart)
    new_order.save()

    # empty the cart
    cart.delete()

    # redirect user to live order page
    return HttpResponseRedirect(reverse("client_app:live_order"))


@login_required(login_url='/login')
def live_order(request):
    
    # check if user is client
    if request.user.is_client is False:
        return render(request, "client_app/error.html", {
            "error": "you must be client to access this page"
        })

    # get order
    try:
        order = Order.objects.get(user=request.user)
    except ObjectDoesNotExist:
        # if there is no order assign order to none
        order = None
    
    # render page with data
    return render(request, "client_app/order.html", {
        "order": order
    })


@login_required(login_url='/login')
def cancel_order(request):

    # make sure request method post
    if request.method != "POST":
        return render(request, "client_app/error.html", {
            "error": "Request Error"
        })

    # check if user is client
    if request.user.is_client is False:
        return render(request, "client_app/error.html", {
            "error": "you must be client to access this page"
        })


    # check if there is order
    try:
        order = Order.objects.get(user=request.user)
    except ObjectDoesNotExist:
        return render(request, "client_app/error.html", {
            "message": "No order"
        })


    # if order got accepted return error
    if order.is_active is True:
        return render(request, "client_app/error.html", {
            "error": "You can't cancel order when accepted"
        })
    
    # remove order from db
    else:
        order.delete()
        
        # redirect to same page
        return HttpResponseRedirect(reverse("client_app:live_order"))


@login_required(login_url='/login')
def old_orders(request):

    # check if user is client
    if request.user.is_client is False:
        return render(request, "client_app/error.html", {
            "error": "you must be client to access this page"
        })

    # get old orders
    old_orders = Old_orders.objects.filter(user=request.user)

    # render template with data
    return render(request, "client_app/old_orders.html", {
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

            # check if user is client
            if user.is_client is False:
                return render(request, "client_app/error.html", {
                    "error": "U must be client to login"
                })
                
            login(request, user)
            return HttpResponseRedirect(reverse("client_app:home"))
        else:
            return render(request, "client_app/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "client_app/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("client_app:index"))


def register(request):
    if request.method == "POST":

        # get inputs from user
        username = request.POST["username"]
        email = request.POST["email"]
        address = request.POST["address"]
        image = request.POST.get("image", "")
        number = request.POST["number"]

        # errors cheking
        if not username or not email or not address or not number:
            return render(request, "client_app/register.html", {
                "message": "Must fill all fields except image"
            })

        if image:
            if len(image) > 200:
                return render(request, "client_app/register.html", {
                    "message": "Image url is too long"
                })

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "client_app/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            if image:
                user = User.objects.create_user(username, email, password)
                user.address = address
                user.image = image
                user.number = number
                user.is_client = True
            else:
                user = User.objects.create_user(username, email, password)
                user.address = address
                user.number = number
                user.is_client = True
            user.save()
        except IntegrityError:
            return render(request, "client_app/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("client_app:home"))
    else:
        return render(request, "client_app/register.html")
