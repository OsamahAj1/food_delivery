from django.db import models
from django.contrib.auth.models import AbstractUser


# class for users
class User(AbstractUser):

    # the following for all users
    is_restaurant = models.BooleanField(default=False)
    is_deliveryperson = models.BooleanField(default=False)
    is_client = models.BooleanField(default=False)

    # image from https://pixabay.com/
    image = models.URLField(max_length=200, default="https://cdn.pixabay.com/photo/2018/11/13/21/43/avatar-3814049_960_720.png")

    # this one for clients and restaurants
    address = models.TextField(blank=True)
    
    # this one for deliverypersons
    car = models.TextField(blank=True)

    # this one for restaurants
    des = models.TextField(blank=True)

    # this one for clients and deliverypersons
    number = models.TextField(blank=True)

    def serialize(self):
        return {
            "username": self.username,
            "email": self.email,
            "number": self.number,
            "image": self.image,
            "car": self.car,
            "address": self.address,
        }


# cart
class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="cart_user")
    item = models.ForeignKey('restaurant_app.Food', on_delete=models.CASCADE, related_name="cart_food")
    n = models.IntegerField()
    sum_price = models.DecimalField(max_digits=6, decimal_places=2)


# old orders
class Old_orders(models.Model):
    restaurant = models.ForeignKey('client_app.User', on_delete=models.CASCADE, related_name="old_orders_user_restaurant")
    deliveryperson = models.ForeignKey('client_app.User', on_delete=models.CASCADE, related_name="old_orders_user_deliveryperson")
    user = models.ForeignKey('client_app.User', on_delete=models.CASCADE, related_name="old_orders_user")
    order = models.TextField()
    sum_order = models.DecimalField(max_digits=6, decimal_places=2)
