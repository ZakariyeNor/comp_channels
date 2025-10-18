from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import AnonymousUser
from .models import Message
import json


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_group_name = 'public_chat'
        await self.channel_layer.group_add(
            self.room_group_name, self.channel_name
        )
        await self.accept()
        await self.send(text_data=json.dumps({'message': 'You are connected to the chat'}))
    
    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name, self.channel_name
        )
    
    async def receive(self, text_data):
        data = json.loads(text_data)
        msg = data.get('message')
        user = self.scope.get('user', None)
        
        message = await self.save_message(user, msg)
        
        await self.channel_layer.group_send(
            self.room_group_name, {
                'type': 'chat_message',
                'user': message.user.username if message.user else "Anon",
                'message': message.content,
            }
        )
        
    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            'user': event['user'],
            'message': event['message'],
        }))
    
    @database_sync_to_async
    def save_message(self, user, content):
        if isinstance(user, AnonymousUser):
            user = None
        return Message.objects.create(user=user, content=content)