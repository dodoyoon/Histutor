from django.db import models
from django import forms

def student_number_validator(value):
   if len(str(value)) != 8:
      raise forms.ValidationError('학번을 다시 입력해주세요')
   
class User(models.Model):
   name = models.CharField(max_length=200)
   nickname = models.CharField(max_length=200, unique=True)
   password = models.CharField(max_length=200)
   student_number = models.IntegerField(unique = True, validators=[student_number_validator])
   phone = models.CharField(max_length=200)
   email = models.EmailField()
   is_tutor = models.NullBooleanField()
   is_staff = models.NullBooleanField()

   def __str__(self):
      return self.name + ' ' + str(self.student_number)
   
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
   tutee_feedback = models.TextField()
   is_confirmed = models.NullBooleanField()

