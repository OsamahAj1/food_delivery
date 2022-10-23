from django.contrib import admin

from client_app.models import User, Cart, Old_orders
from deliveryperson_app.models import Order
from restaurant_app.models import Food


class CartAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "item")


class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "restaurant", "deliveryperson", "user", "order", "sum_order", "is_active")


class FoodAdmin(admin.ModelAdmin):
    list_display = ("id", "restaurant", "food", "des", "price", "image")


class UserAdmin(admin.ModelAdmin):
    list_display = ("id", "username", "email", "is_restaurant", "is_deliveryperson", "address", "car", "des", "image")

class Old_ordersAdmin(admin.ModelAdmin):
    list_display = ("id", "restaurant", "deliveryperson", "user", "order", "sum_order")


admin.site.register(Cart, CartAdmin)
admin.site.register(Order, OrderAdmin)
admin.site.register(Food, FoodAdmin)
admin.site.register(User, UserAdmin)
admin.site.register(Old_orders, Old_ordersAdmin)
