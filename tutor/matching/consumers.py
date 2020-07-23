import json
from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
from matching import models as matching_models

class NewPostConsumer(WebsocketConsumer):
    def connect(self):
        self.group_name = 'new_post'

        # Join room group
        async_to_sync(self.channel_layer.group_add)(
            self.group_name,
            self.channel_name
        )

        self.accept()

    def disconnect(self, close_code):
        # Leave room group
        async_to_sync(self.channel_layer.group_discard)(
            self.group_name,
            self.channel_name
        )

    # Receive message from WebSocket
    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        id = text_data_json['id']
        title = text_data_json['title']
        finding = text_data_json['finding']
        pub_date = text_data_json['pub_date']
        topic = text_data_json['topic']
        nickname = text_data_json['nickname']

        # Send message to room group
        async_to_sync(self.channel_layer.group_send)(
            self.group_name,
            {
                'type': 'new_post',
                'id': id,
                'title': title,
                'finding': finding,
                'pub_date': pub_date,
                'topic': topic,
                'nickname': nickname,
            }
        )

    # Receive message from room group
    def new_post(self, event):
        id = event['id']
        title = event['title']
        finding = event['finding']
        pub_date = event['pub_date']
        nickname = event['nickname']

        # Send message to WebSocket
        self.send(text_data=json.dumps({
            'type': 'new_post',
            'id': id,
            'title': title,
            'finding': finding,
            'pub_date': pub_date,
            'nickname': nickname,
        }))

class PostDetailConsumer(WebsocketConsumer):
    def connect(self):
        self.group_name = 'new_comment'

        # Join room group
        async_to_sync(self.channel_layer.group_add)(
            self.group_name,
            self.channel_name
        )

        self.accept()

    def disconnect(self, close_code):
        # Leave room group
        async_to_sync(self.channel_layer.group_discard)(
            self.group_name,
            self.channel_name
        )

    # Receive message from WebSocket
    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        post_id = text_data_json['postId']

        # Send message to room group
        async_to_sync(self.channel_layer.group_send)(
            self.group_name,
            {
                'type': 'new_comment',
                'id': post_id,
            }
        )

    # Receive message from room group
    def new_comment(self, event):
        id = event['id']
        comment = matching_models.Comment.objects.get(pk=id)
        username = comment.user.username
        date = comment.pub_date

        # Send message to WebSocket
        self.send(text_data=json.dumps({
            'type': 'new_comment',
            'id': id,
            'content': comment.content,
            'username': username,
            'date': str(date),
        }))