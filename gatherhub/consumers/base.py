"""
Base WebSocket consumer with authentication and common functionality.
"""

import json
import logging
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import AnonymousUser
from rest_framework_simplejwt.tokens import UntypedToken
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist

User = get_user_model()
logger = logging.getLogger(__name__)


class BaseConsumer(AsyncWebsocketConsumer):
    """Base WebSocket consumer with authentication and room management."""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = None
        self.room_group_name = None
        self.event_slug = None
        
    async def connect(self):
        """Handle WebSocket connection with JWT authentication."""
        try:
            # Extract token from query string or headers
            token = await self.get_token()
            if not token:
                await self.close(code=4001)  # Unauthorized
                return
                
            # Authenticate user
            self.user = await self.authenticate_token(token)
            if not self.user:
                await self.close(code=4001)  # Unauthorized
                return
                
            # Extract event slug from URL
            self.event_slug = self.scope['url_route']['kwargs'].get('event_slug')
            if not self.event_slug:
                await self.close(code=4002)  # Bad Request
                return
                
            # Check event access permissions
            if not await self.check_event_access():
                await self.close(code=4003)  # Forbidden
                return
                
            # Set up room group
            self.room_group_name = await self.get_room_group_name()
            
            # Join room group
            if self.channel_layer:
                await self.channel_layer.group_add(
                    self.room_group_name,
                    self.channel_name
                )
            
            await self.accept()
            
            # Send connection confirmation
            await self.send_json({
                'type': 'connection_established',
                'data': {
                    'room': self.room_group_name,
                    'user_id': self.user.id,
                    'event_slug': self.event_slug
                }
            })
            
            logger.info(f"User {self.user.id} connected to room {self.room_group_name}")
            
        except Exception as e:
            logger.error(f"Connection error: {str(e)}")
            await self.close(code=4000)  # Internal Server Error
    
    async def disconnect(self, code):
        """Handle WebSocket disconnection."""
        if self.room_group_name and self.channel_layer:
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )
            
            if self.user:
                logger.info(f"User {self.user.id} disconnected from room {self.room_group_name}")
    
    async def receive(self, text_data=None, bytes_data=None):
        """Handle incoming WebSocket messages."""
        if text_data is None:
            return
        try:
            data = json.loads(text_data)
            message_type = data.get('type')
            
            # Route message to appropriate handler
            handler_name = f'handle_{message_type}'
            if hasattr(self, handler_name):
                handler = getattr(self, handler_name)
                await handler(data)
            else:
                await self.send_error('Unknown message type', message_type)
                
        except json.JSONDecodeError:
            await self.send_error('Invalid JSON format')
        except Exception as e:
            logger.error(f"Message handling error: {str(e)}")
            await self.send_error('Internal server error')
    
    async def get_token(self):
        """Extract JWT token from query string or subprotocol."""
        # Try query string first
        query_string = self.scope.get('query_string', b'').decode()
        if 'token=' in query_string:
            for param in query_string.split('&'):
                if param.startswith('token='):
                    return param.split('=', 1)[1]
        
        # Try subprotocols (for browsers that support it)
        subprotocols = self.scope.get('subprotocols', [])
        for protocol in subprotocols:
            if protocol.startswith('access_token.'):
                return protocol.split('.', 1)[1]
        
        return None
    
    @database_sync_to_async
    def authenticate_token(self, token):
        """Authenticate JWT token and return user."""
        try:
            # Validate token
            UntypedToken(token)
            
            # Decode token to get user
            from rest_framework_simplejwt.authentication import JWTAuthentication
            jwt_auth = JWTAuthentication()
            validated_token = jwt_auth.get_validated_token(token)
            user = jwt_auth.get_user(validated_token)
            
            if user and user.is_active:
                return user
            return None
            
        except (InvalidToken, TokenError, Exception):
            return None
    
    @database_sync_to_async
    def check_event_access(self):
        """Check if user can access the event. Override in subclasses."""
        from apps.events.models import Event
        try:
            event = Event.objects.get(slug=self.event_slug)
            # For now, allow access to all authenticated users
            # This can be enhanced with proper permission checking
            return True
        except Event.DoesNotExist:
            return False
    
    async def get_room_group_name(self):
        """Get the room group name. Override in subclasses."""
        return f"event_{self.event_slug}"
    
    async def send_json(self, content):
        """Send JSON message to WebSocket."""
        await self.send(text_data=json.dumps(content))
    
    async def send_error(self, message, details=None):
        """Send error message to client."""
        error_data = {
            'type': 'error',
            'data': {
                'message': message,
                'timestamp': self.get_timestamp()
            }
        }
        if details:
            error_data['data']['details'] = details
        await self.send_json(error_data)
    
    def get_timestamp(self):
        """Get current timestamp in ISO format."""
        from django.utils import timezone
        return timezone.now().isoformat()
    
    # Group message handlers
    async def broadcast_message(self, event):
        """Handle broadcast messages from group."""
        await self.send_json(event['message'])
