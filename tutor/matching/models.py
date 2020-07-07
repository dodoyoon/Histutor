from django.db import models

class User(models.Model):
   name = models.CharField(max_length=200, null=True)
   nickname = models.CharField(max_length=200, null=True)
   password = models.CharField(max_length=200, null=True)
   student_number = models.IntegerField(null=True)
   phone = models.CharField(max_length=200, null=True)
   email = models.EmailField(null=True)
   is_tutor = models.NullBooleanField(default=False)
   is_staff = models.NullBooleanField(default=False)
   
class Topic(models.Model):
   name = models.CharField(max_length=200)

class Post(models.Model):
   user = models.ForeignKey(User, on_delete=models.CASCADE)
   topic = models.ForeignKey(Topic, on_delete=models.CASCADE)
   title = models.CharField(max_length=200)
   content = models.TextField()
   finding_match = models.NullBooleanField(default=False)
   pub_date = models.DateTimeField(auto_now_add=True)
   cancel_reason = models.TextField(null=True)

class Comment(models.Model):
   user = models.ForeignKey(User, on_delete=models.CASCADE)
   post = models.ForeignKey(Post, on_delete=models.CASCADE)
   pub_date = models.DateTimeField(auto_now_add=True)
   content = models.TextField()
   
class Report(models.Model):
   tutor = models.ForeignKey(User, on_delete=models.CASCADE, related_name="tutor")
   tutee = models.ForeignKey(User, on_delete=models.CASCADE, related_name="tutee")
   post = models.ForeignKey(Post, on_delete=models.CASCADE)
   meeting_date = models.DateTimeField()
   meeting_duration_time = models.IntegerField()
   pub_date = models.DateTimeField(auto_now_add=True)
   tutee_feedback = models.TextField(null=True)
   is_confirmed = models.NullBooleanField(default=False)
   content = models.TextField()
