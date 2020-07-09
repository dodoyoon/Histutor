from django.db import models
from django import forms
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class Profile(models.Model):
   user = models.OneToOneField(User, on_delete=models.CASCADE)
   nickname = models.CharField(null=True,max_length=200, unique=True)
   phone = models.CharField(null=True, blank=True,max_length=200)
   is_tutor = models.BooleanField(null=True,blank=True)
   signin = models.BooleanField(default=False)

   def __str__(self):
      return self.user.username + ' ' + self.user.last_name

   @receiver(post_save, sender=User)
   def create_user_profile(sender, instance, created, **kwargs):
      if created:
         Profile.objects.create(user=instance)

   @receiver(post_save, sender=User)
   def save_user_profile(sender, instance, **kwargs):
      instance.profile.save()

class Topic(models.Model):
   name = models.CharField(max_length=200)

class Post(models.Model):
   user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="post_relation")
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
   content = models.TextField()

