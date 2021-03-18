import json
#from channels.generic.websocket import WebsocketConsumer  --->Synchronous way
from channels.generic.websocket import AsyncWebsocketConsumer #Asynchronous way
#from asgiref.sync import async_to_sync
from django.utils import timezone

"""
Below are synchronous way to establish web server


class ChatConsumer(WebsocketConsumer):
    def connect(self):    
        self.user = self.scope['user']
        self.id = self.scope['url_route']['kwargs']['course_id']
        self.room_group_name = 'chat_%s' %self.id
        
        #Import the async_to_sync() helper function to wrap calls to asynchronous channel layer methods. 
        #ChatConsumer is a synchronous WebsocketConsumer consumer, 
        #but it needs to call asynchronous methods of the channel layer.

        # Join room group
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name
        )
        # Accept connection
        self.accept()
    
    def disconnect(self, close_code):
        # Leave room group
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name,
            self.channel_name
        )

    # Receive message from websocket
    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        now = timezone.now()
        # Send message to room group
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'user': self.user.username,
                'datetime': now.isoformat(),
            }
        )
    
    # Receive message from room group
    def chat_message(self, event):
        # Send message to Websocket
        self.send(text_data=json.dumps(event))

"""

# Asynchronous way

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):    
        self.user = self.scope['user']
        self.id = self.scope['url_route']['kwargs']['course_id']
        self.room_group_name = 'chat_%s' %self.id
        """
        Import the async_to_sync() helper function to wrap calls to asynchronous channel layer methods. 
        ChatConsumer is a synchronous WebsocketConsumer consumer, 
        but it needs to call asynchronous methods of the channel layer.
        """
        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        # Accept connection
        await self.accept()
    
    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    # Receive message from websocket
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        now = timezone.now()
        # Send message to room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'user': self.user.username,
                'datetime': now.isoformat(),
            }
        )
    
    # Receive message from room group
    async def chat_message(self, event):
        # Send message to Websocket
        await self.send(text_data=json.dumps(event))
