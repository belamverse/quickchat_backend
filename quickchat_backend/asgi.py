import os
from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application
from channels.auth import AuthMiddlewareStack  

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'quickchat_backend.settings')

# Initialize Django
django_application = get_asgi_application()

# Import after initializing Django
import chat.routing

application = ProtocolTypeRouter({
    "http": django_application,
    "websocket": AuthMiddlewareStack(
        URLRouter(
            chat.routing.websocket_urlpatterns
        )
    ),
})