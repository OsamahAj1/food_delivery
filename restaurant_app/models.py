from django.db import models


# restaurant food
class Food(models.Model):
    restaurant = models.ForeignKey('client_app.User', on_delete=models.CASCADE, related_name="food_user")
    food = models.TextField()
    image = models.URLField(max_length=200)
    des = models.TextField()
    price = models.DecimalField(max_digits=6, decimal_places=2)

    def __str__(self):
        return f"{self.food} from {self.restaurant}"
