from django.urls import path
from . import views

app_name = "client_app"

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("home", views.home, name="home"),
    path("restaurant/<str:res>", views.restaurant, name="restaurant"),
    path("cart", views.cart, name="cart"),
    path("place_order", views.place_order, name="place_order"),
    path("live_order", views.live_order, name="live_order"),
    path("cancel_order", views.cancel_order, name="cancel_order"),
    path("old_orders", views.old_orders, name="old_orders"),

    # API routes
    path("add_cart/<int:food_id>", views.add_cart, name="add_cart"),
    path("update_cart/<int:cart_id>", views.update_cart, name="update_cart"),
    path("remove_cart/<int:cart_id>", views.remove_cart, name="remove_cart"),
    path("sum_cart", views.sum_cart, name="sum_cart"),

]