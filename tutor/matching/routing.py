from django.urls import re_path

from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/tutorhome/$', consumers.NewPostConsumer),
    re_path(r'ws/post/(?P<postId>\d+)/$', consumers.PostDetailConsumer),
    re_path(r'ws/session/(?P<sessionId>\d+)/$', consumers.SessionDetailConsumer),
]
