import json
from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
from matching import models as matching_models
from django.utils import timezone

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
        startTime = text_data_json['startTime']
        endTime = text_data_json['endTime']
        postUser = text_data_json['postUser']
        tutor = text_data_json['tutor']
        reportExist = text_data_json['reportExist']

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
                'startTime': startTime,
                'endTime': endTime,
                'postUser': postUser,
                'tutor': tutor,
                'reportExist': reportExist,
            }
        )

    # Receive message from room group
    def new_post(self, event):
        id = event['id']
        post = matching_models.Post.objects.get(pk=id)
        title = event['title']
        finding = event['finding']
        pub_date = timezone.localtime(post.pub_date).strftime("%H:%M")
        nickname = event['nickname']
        startTime = event['startTime']
        endTime = event['endTime']
        postUser = event['postUser']
        tutor = event['tutor']
        reportExist = event['reportExist']
        hit = event['hit']

        # Send message to WebSocket
        self.send(text_data=json.dumps({
            'type': 'new_post',
            'id': id,
            'title': title,
            'finding': finding,
            'pub_date': pub_date,
            'nickname': nickname,
            'startTime': startTime,
            'endTime': endTime,
            'postUser': postUser,
            'tutor': tutor,
            'reportExist': reportExist,
            'hit': hit,
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
        db_date = comment.pub_date
        time = timezone.localtime(db_date).strftime("%-I:%M")
        am_or_pm = timezone.localtime(db_date).strftime("%p").lower()
        am_or_pm = am_or_pm[0] + '.' + am_or_pm[1] + '.'
        date = time + ' ' + am_or_pm
        profile = matching_models.Profile.objects.get(user=comment.user)

        # Send message to WebSocket
        self.send(text_data=json.dumps({
            'type': 'new_comment',
            'id': id,
            'content': comment.content,
            'username': username,
            'date': date,
            'nickname': profile.nickname,
        }))

    # Receive message from room group
    def star_comment(self, event):
        id = event['id']
        comment = matching_models.Comment.objects.get(pk=id)

        # Send message to WebSocket
        self.send(text_data=json.dumps({
            'type': 'star_comment',
            'id': id,
            'content': comment.content,
            'username': comment.user.username,
        }))

class SessionDetailConsumer(WebsocketConsumer):
    def connect(self):
        self.group_name = 'new_comment_session'

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
        type = text_data_json['type']

        if type == "new_comment":
          comment_id = text_data_json['comment_id']

          # Send message to room group
          async_to_sync(self.channel_layer.group_send)(
              self.group_name,
              {
                  'type': 'new_comment',
                  'id': comment_id,
              }
          )
        elif type == "start_new_tutoring":
          next_tutee_pk = text_data_json['next_tutee_pk']
          next_tutee_url = text_data_json['next_tutee_url']
          async_to_sync(self.channel_layer.group_send)(
              self.group_name,
              {
                  'type': 'get_next_tutee',
                  'pk': next_tutee_pk,
                  'next_tutee_url': next_tutee_url
              }
          )

    # Receive message from room group
    def new_comment(self, event):
        id = event['id']
        comment = matching_models.Comment.objects.get(pk=id)
        username = comment.user.username
        db_date = comment.pub_date
        time = timezone.localtime(db_date).strftime("%-I:%M")
        am_or_pm = timezone.localtime(db_date).strftime("%p").lower()
        am_or_pm = am_or_pm[0] + '.' + am_or_pm[1] + '.'
        date = time + ' ' + am_or_pm
        profile = matching_models.Profile.objects.get(user=comment.user)

        # Send message to WebSocket
        self.send(text_data=json.dumps({
            'type': 'new_comment',
            'id': id,
            'content': comment.content,
            'username': username,
            'date': date,
            'nickname': profile.nickname,
        }))

    # Receive message from room group
    def star_comment(self, event):
        id = event['id']
        comment = matching_models.Comment.objects.get(pk=id)

        # Send message to WebSocket
        self.send(text_data=json.dumps({
            'type': 'star_comment',
            'id': id,
            'content': comment.content,
            'username': comment.user.username,
        }))
    
    def get_next_tutee(self, event):
      pk = event['pk']
      log = matching_models.SessionLog.objects.get(pk = pk)

      self.send(text_data=json.dumps({
        'type': 'get_next_tutee',
        'next_tutee_pk': log.tutee.pk,
        'session_pk': log.tutor_session.pk,
        'next_tutee_url': event['next_tutee_url'],
      }))