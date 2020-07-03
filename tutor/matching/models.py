from django.db import models

class User(models.Model):
   name = models.CharField(max_length=200)
   nickname = models.CharField(max_length=200)
   password = models.CharField(max_length=200)
   student_number = models.IntegerField()
   contact = models.CharField(max_length=200)
   email = models.EmailField()
   is_tutor = models.NullBooleanField()
   is_staff = models.NullBooleanField()
   
class Topic(models.Model):
   name = models.CharField(max_length=200)

class Post(models.Model):
   user = models.ForeignKey(User, on_delete=models.CASCADE)
   topic = models.ForeignKey(Topic, on_delete=models.CASCADE)
   title = models.CharField(max_length=200)
   content = models.TextField()
   finding_match = models.NullBooleanField()
   post_time = models.DateTimeField(auto_now_add=True)
   cancel_reason = models.TextField()

class Comment(models.Model):
   user = models.ForeignKey(User, on_delete=models.CASCADE)
   post = models.ForeignKey(Post, on_delete=models.CASCADE)
   time = models.DateTimeField(auto_now_add=True)
   content = models.TextField()
   
class Report(models.Model):
   tutor = models.ForeignKey(User, on_delete=models.CASCADE, related_name="tutor")
   tutee = models.ForeignKey(User, on_delete=models.CASCADE, related_name="tutee")
   post = models.ForeignKey(Post, on_delete=models.CASCADE)
   meeting_time = models.DateTimeField()
   meeting_duration_time = models.IntegerField()
   report_time = models.DateTimeField(auto_now_add=True)
   tutee_feedback = models.TextField()
   is_confirmed = models.NullBooleanField()
