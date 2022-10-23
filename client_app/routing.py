from django.urls import path
from . import consumers

websocket_urlpatterns = [
    path('ws/place/<str:index>/', consumers.PlaceConsumer.as_asgi()),
    path('ws/accept/<str:order>/', consumers.AcceptConsumer.as_asgi()),
    path('ws/res/<str:res>/', consumers.RestaurantConsumer.as_asgi()),
]