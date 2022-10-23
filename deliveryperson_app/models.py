from django.db import models


# orders table
class Order(models.Model):
    restaurant = models.ForeignKey('client_app.User', on_delete=models.CASCADE, related_name="order_user_restaurant")
    deliveryperson = models.ForeignKey('client_app.User', on_delete=models.CASCADE, related_name="order_user_deliveryperson", blank=True, null=True)
    user = models.ForeignKey('client_app.User', on_delete=models.CASCADE, related_name="order_user")
    order = models.TextField()
    sum_order = models.DecimalField(max_digits=6, decimal_places=2)
    is_active = models.BooleanField(default=False)
    is_sent = models.BooleanField(default=False)

    def serialize(self):

        if self.deliveryperson is None:
            return {
                "id": self.id,
                "restaurant": self.restaurant.serialize(),
                "user": self.user.serialize(),
                "order": self.order,
                "sum_order": self.sum_order,
            }
        
        else:
            return {
                "id": self.id,
                "restaurant": self.restaurant.serialize(),
                "deliveryperson": self.deliveryperson.serialize(),
                "user": self.user.serialize(),
                "order": self.order,
                "sum_order": self.sum_order,
            }
