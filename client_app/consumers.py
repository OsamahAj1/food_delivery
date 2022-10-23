import json

from channels.generic.websocket import AsyncJsonWebsocketConsumer
from asgiref.sync import sync_to_async
from deliveryperson_app.models import Order
from client_app.models import User
from channels.db import database_sync_to_async
from django.core.exceptions import ObjectDoesNotExist

class PlaceConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        self.index = self.scope["url_route"] ['kwargs'] ['index']
        self.index_group_name = 'index_%s' % self.index

        await self.channel_layer.group_add(
            self.index_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, e):
        await self.channel_layer.group_discard(
            self.index_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
       data = json.loads(text_data)

       await self.update_order(data["order_id"])
   
       await self.channel_layer.group_send(
           self.index_group_name,
           {
               "type": "order_info",
               "res_img": data["res_img"],
               "res_name": data["res_name"],
               "res_adr": data["res_adr"],
               "res_id": data["res_id"],
               "order": data["order"],
               "sum_order": data["sum_order"],
               "order_id": data["order_id"],
               "user_adr": data["user_adr"],
           }
       )

    async def order_info(self, event):

        await self.send(text_data=json.dumps({
            "res_img": event["res_img"],
            "res_name": event["res_name"],
            "res_adr": event["res_adr"],
            "res_id": event["res_id"],
            "order": event["order"],
            "sum_order": event["sum_order"],
            "order_id": event["order_id"],
            "user_adr": event["user_adr"],
        }))


    @sync_to_async
    def update_order(self, order_id):
        order_id = int(order_id)
        order = Order.objects.get(pk=order_id)
        order.is_sent = True
        order.save()


class AcceptConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        self.order = self.scope["url_route"]['kwargs']['order']
        self.order_group_name = 'order_%s' % self.order

        await self.channel_layer.group_add(
            self.order_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, e):
        await self.channel_layer.group_discard(
            self.order_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
       data = json.loads(text_data)

       check = await self.check(self.order, data["del_id"])
       print(check)
       if not check:
        print("oh noooo")

        await self.channel_layer.group_send(
            self.order_group_name,
            {
                "type": "error_info",
                "error": "Error",
            }
        )

       else:
        print("oh yeeeee babye ")

        await self.update_order(self.order, data["del_id"])

        await self.channel_layer.group_send(
            self.order_group_name,
            {
                "type": "delivery_info",
                "del_img": data["del_img"],
                "del_name": data["del_name"],
                "del_car": data["del_car"],
                "del_number": data["del_number"],
            }
        )

    async def delivery_info(self, event):

        await self.send(text_data=json.dumps({
            "del_img": event["del_img"],
            "del_name": event["del_name"],
            "del_car": event["del_car"],
            "del_number": event["del_number"],
        }))

    async def error_info(self, event):

        await self.send(text_data=json.dumps({
            "error": event["error"],
        }))

    @sync_to_async
    def update_order(self, order_id, del_id):
        order_id = int(order_id)
        del_id = int(del_id)
        delivery = User.objects.get(pk=del_id)
        order = Order.objects.get(pk=order_id)
        order.is_active = True
        order.deliveryperson = delivery
        order.save()

    @database_sync_to_async
    def check(self, order_id, del_id):

        order = Order.objects.filter(pk=int(order_id)).first()

        delivery = User.objects.get(pk=int(del_id))

        if not order:
            return False
        
        if order.deliveryperson:
            return False

        try:
            Order.objects.get(deliveryperson=delivery)
            return False
        except ObjectDoesNotExist:
            pass
        
        return True


class RestaurantConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        self.res = self.scope["url_route"]['kwargs']['res']
        self.res_group_name = 'res_%s' % self.res

        await self.channel_layer.group_add(
            self.res_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, e):
        await self.channel_layer.group_discard(
            self.res_group_name,
            self.channel_name
        )

    async def receive(self, text_data): 
       data = json.loads(text_data)

       await self.channel_layer.group_send(
           self.res_group_name,
           {
               "type": "order_info",
               "order_id": data["order_id"],
               "del_name": data["del_name"],
               "order_order": data["order_order"],
               "sum_order": data["sum_order"],
           }
       )

    async def order_info(self, event):

        await self.send(text_data=json.dumps({
            "order_id": event["order_id"],
            "del_name": event["del_name"],
            "order_order": event["order_order"],
            "sum_order": event["sum_order"],
        }))



