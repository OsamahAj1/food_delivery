from django.urls import path
from . import views

app_name = "deliveryperson_app"

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("live_order", views.live_order, name="live_order"),
    path("delivered", views.delivered, name="delivered"),
    path("old_orders", views.old_orders, name="old_orders"),
]