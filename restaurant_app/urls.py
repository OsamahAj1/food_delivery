from django.urls import path
from . import views

app_name = "restaurant_app"

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("add_food", views.add_food, name="add_food"),
]