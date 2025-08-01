# chat/middleware.py
from urllib.parse import parse_qs
from django.contrib.auth.models import AnonymousUser
from django.db import close_old_connections
from channels.db import database_sync_to_async
from rest_framework_simplejwt.tokens import AccessToken
from django.contrib.auth import get_user_model

User = get_user_model()

@database_sync_to_async
def get_user_by_token(token_key):
    try:
        access_token = AccessToken(token_key)
        user = User.objects.get(id=access_token['user_id'])
        return user
    except Exception as e:
        print(f"Token validation failed: {e}")
        return AnonymousUser()

class TokenAuthMiddleware:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        # Close old connections to prevent issues with stale connections
        close_old_connections()
        
        try:
            # Get the token from the query string
            query_string = parse_qs(scope["query_string"].decode("utf8"))
            token = query_string.get("token", [None])[0]
            
            if token:
                # Validate the token and get the user
                scope["user"] = await get_user_by_token(token)
            else:
                scope["user"] = AnonymousUser()

        except Exception as e:
            print(f"Error getting user from token: {e}")
            scope["user"] = AnonymousUser()
        
        return await self.app(scope, receive, send)