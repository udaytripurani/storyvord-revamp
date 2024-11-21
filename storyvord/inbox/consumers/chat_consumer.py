import json
from channels.generic.websocket import AsyncWebsocketConsumer
from inbox.models import DialogsModel, MessageModel, RoomModel
from accounts.models import User
from channels.db import database_sync_to_async
from rest_framework_simplejwt.tokens import AccessToken
from django.core.cache import cache


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        print(f"Connecting to path: {self.scope['path']}")
        # Extract access token from the query string
        query_string = self.scope.get('query_string').decode("utf-8")
        access_token = self._get_query_param(query_string, 'access_token')
        
        try:
            # Authenticate user using the access token
            self.user = await self.get_user_from_token(access_token)
            print(self.user)
        except Exception as e:
            print(f"Error: {e}")
            await self.close()
            return
        
        self.room_type = self.scope["url_route"]["kwargs"]["type"]  # "user" or "room"
        self.room_id = self.scope["url_route"]["kwargs"]["id"]
        
        if not self.user.is_authenticated:
            await self.close()
            return
        
        if self.room_type == "user":
            self.room_group_name = f"chat_user_{min(self.user.id, int(self.room_id))}_{max(self.user.id, int(self.room_id))}"
        else:  # Room chat
            self.room_group_name = f"chat_room_{self.room_id}"

        try:
            await self.set_user_online(self.user.id)
        except Exception as e:
            print(f"Error setting user online: {e}")
            await self.close()
            return

        # Notify other users in the group that this user is online
        try:
            await self.channel_layer.group_add(
                self.room_group_name,
                self.channel_name
            )
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'online_status',
                    'user_id': str(self.user.id),
                    'status': 'online'
                }
            )
        except Exception as e:
            print(f"Error sending online status: {e}")
            await self.close()
            return

        await self.accept()

    async def disconnect(self, close_code):
        # Mark user as offline in in-memory cache
        await self.set_user_offline(self.user.id)

        # Notify other users that this user is offline
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'online_status',
                'user_id': str(self.user.id),
                'status': 'offline'
            }
        )

        # Leave the room group when the WebSocket is disconnected
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        data = json.loads(text_data)
        message_text = data.get('message', '')
        
        if self.room_type == "user":
            recipient = await database_sync_to_async(User.objects.get)(id=self.room_id)
            message = await database_sync_to_async(MessageModel.objects.create)(
                sender=self.user, recipient=recipient, text=message_text
            )
        else:  # Room chat
            room = await database_sync_to_async(RoomModel.objects.get)(id=self.room_id)
            message = await database_sync_to_async(MessageModel.objects.create)(
                sender=self.user, room=room, text=message_text
            )
        
        # Send the message to the room group with detailed user info
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message_text,
                'sender': self.user.id,
                'sender_info': await self.get_user_info(self.user.id),
            }
        )
        
        if 'typing' in data:
            # Handle typing event
            typing_status = data['typing']

            # Send typing event to the room group
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'typing_status',
                    'typing': typing_status,
                    'sender': str(self.user.id),
                }
            )

    async def chat_message(self, event):
        message = event['message']
        sender = event['sender']

        # Send the message to the WebSocket
        await self.send(text_data=json.dumps({
            'message': message,
            'sender': sender,
        }))

    async def typing_status(self, event):
        typing = event['typing']
        sender = event['sender']
        you = event['you']

        # Send the typing status to the WebSocket
        await self.send(text_data=json.dumps({
            'typing': typing,
            'sender': sender,
            'you': you
        }))

    async def online_status(self, event):
        user_id = event['user_id']
        status = event['status']

        # Send the online/offline status to the WebSocket
        await self.send(text_data=json.dumps({
            'user_id': user_id,
            'status': status
        }))

    def _get_query_param(self, query_string, param):
        params = dict(p.split('=') for p in query_string.split('&'))
        return params.get(param, None)

    @database_sync_to_async
    def get_user_from_token(self, access_token):
        # Implement token validation and user retrieval logic here
        try:
            token = AccessToken(access_token)
            user_id = token.payload['user_id']
            return User.objects.get(id=user_id)
        except (User.DoesNotExist, KeyError):
            return None

    @database_sync_to_async
    def set_user_online(self, user_id):
        # Set user as online in in-memory cache
        cache.set(f'user_{user_id}_online', True)

    @database_sync_to_async
    def set_user_offline(self, user_id):
        # Set user as offline in in-memory cache
        cache.set(f'user_{user_id}_online', False)

    @database_sync_to_async
    def is_user_online(self, user_id):
        # Check if a user is online from in-memory cache
        return cache.get(f'user_{user_id}_online', False)

    @database_sync_to_async
    def get_user_info(self, user_id):
        """
        Fetch user details and format as needed for WebSocket messages.
        """
        try:
            user = User.objects.get(id=user_id)
            return {
                'id': user.id,
                'email': user.email,
                'user_type': user.user_type,
                'name': self.get_user_name(user),
                'you': user_id == self.user.id
            }
        except User.DoesNotExist:
            return None

    def get_user_name(self, user):
        """
        Get the name of the user based on their profile.
        """
        if user.user_type == '1':
            profile = getattr(user, 'clientprofile', None)
            return f"{profile.firstName} {profile.lastName}" if profile else None
        elif user.user_type == '2':
            profile = getattr(user, 'crewprofile', None)
            return profile.name if profile else None
        return None
