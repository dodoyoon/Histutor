from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
import matching.routing

application = ProtocolTypeRouter({
    # (http->django views is added by default)
    'websocket': AuthMiddlewareStack(
        URLRouter(
            matching.routing.websocket_urlpatterns
        )
    ),
})

ASGI_APPLICATION = "tutor.routing.application"
