import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.utils.timezone import now
from .models import ChatMessage, Room 
from django.contrib.auth import get_user_model

User = get_user_model()

class ChatConsumer(AsyncWebsocketConsumer):
    # Class attributes are no longer needed for room_group_name
    
    async def connect(self):
        """
        Called when a WebSocket connection is established.
        """
        # Get the room name from the URL path
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f'chat_{self.room_name}'
        
        # Check if the room exists in the database
        try:
            self.room = await self.get_room()
        except Room.DoesNotExist:
            print(f"Room '{self.room_name}' does not exist. Closing connection.")
            await self.close()
            return
        
        # Join the room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        await self.accept()
        
        await self.send(text_data=json.dumps({
            'message': f'WebSocket connected to room {self.room_name}',
            'status': 'connected'
        }))

    async def disconnect(self, close_code):
        """
        Called when a WebSocket connection is closed.
        """
        # Leave the room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
        print(f"WebSocket disconnected from room {self.room_name} with close code: {close_code}")

    async def receive(self, text_data):
        """
        Called when a message is received from the WebSocket.
        """
        data = json.loads(text_data)
        message = data.get('message')
        user = self.scope['user']

        if user.is_authenticated and message:
            # We use self.room which was fetched in the connect method
            chat_message_obj = await self.create_chat_message(user, self.room, message)
            
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'user': user.username,
                    'message': message,
                    'timestamp': chat_message_obj.timestamp.strftime('%Y-%m-%d %H:%M:%S')
                }
            )
        else:
            await self.send(text_data=json.dumps({
                'error': 'User not authenticated or invalid message format.'
            }))
            await self.close()

    @database_sync_to_async
    def get_room(self):
        """
        Fetches the room object from the database asynchronously.
        """
        return Room.objects.get(name=self.room_name)

    @database_sync_to_async
    def create_chat_message(self, user, room, message):
        """
        Synchronous function to create a new chat message in the database.
        """
        return ChatMessage.objects.create(user=user, room=room, message=message)

    async def chat_message(self, event):
        """
        Receive message from the room group and forward it to the WebSocket.
        """
        message = event['message']
        user = event['user']
        timestamp = event['timestamp']
        
        await self.send(text_data=json.dumps({
            'user': user,
            'message': message,
            'timestamp': timestamp
        }))