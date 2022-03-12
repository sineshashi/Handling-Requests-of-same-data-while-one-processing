import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.exceptions import StopConsumer

class MyConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        pk = self.scope['url_route']['kwargs']['pk']
        group_name = f'post{pk}'
        await self.channel_layer.group_add(group_name, self.channel_name)
        await self.accept()

    async def websocket_receive(self, message):
        pk = self.scope['url_route']['kwargs']['pk']
        group_name = f'post{pk}'
        await self.channel_layer.group_send(group_name, {
            'type': 'send.post',
            'post_data': message
        })

    async def send_post(self, event):
        await self.send(event['post_data'])
        await self.close()


    async def websocket_disconnect(self, message):
        pk = self.scope['url_route']['kwargs']['pk']
        group_name = f'post{pk}'
        await self.channel_layer.group_discard(group_name, self.channel_name)
        raise StopConsumer()
