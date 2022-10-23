from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include("client_app.urls")),
    path('delivery_person/', include("deliveryperson_app.urls")),
    path('restaurants/', include("restaurant_app.urls")),
]
