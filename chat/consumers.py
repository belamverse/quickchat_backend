import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.utils.timezone import now
from .models import ChatMessage, Room 
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser

User = get_user_model()

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        """
        Called when a WebSocket connection is established.
        """
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f'chat_{self.room_name}'
        
        self.user = self.scope['user']
        
        if isinstance(self.user, AnonymousUser):
            print("Unauthenticated user attempted to connect. Closing connection.")
            await self.close(code=1000)
            return
            
        try:
            self.room = await self.get_room()
            # Changed the log message to use email
            print(f"User '{self.user.email}' connected to room '{self.room_name}'.")
        except Room.DoesNotExist:
            print(f"Room '{self.room_name}' does not exist. Closing connection.")
            await self.close()
            return
        except Exception as e:
            print(f"An unexpected error occurred during connection: {e}")
            await self.close()
            return
        
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
        if isinstance(self.user, User):
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
        
        if isinstance(self.user, User) and message:
            chat_message_obj = await self.create_chat_message(self.user, self.room, message)
            
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'user': self.user.first_name or self.user.email,
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
        return Room.objects.get(name=self.room_name)

    @database_sync_to_async
    def create_chat_message(self, user, room, message):
        return ChatMessage.objects.create(user=user, room=room, message=message)

    async def chat_message(self, event):
        message = event['message']
        user = event['user']
        timestamp = event['timestamp']
        
        await self.send(text_data=json.dumps({
            'user': user,
            'message': message,
            'timestamp': timestamp
        }))