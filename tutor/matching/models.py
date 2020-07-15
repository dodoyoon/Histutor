from django.db import models
from django import forms
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.urls import reverse

class Profile(models.Model):
   user = models.OneToOneField(User, on_delete=models.CASCADE)
   nickname = models.CharField(null=True,max_length=200, unique=True)
   phone = models.CharField(null=True, blank=True,max_length=200)
   is_tutor = models.BooleanField(null=True,blank=True, default=False)
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


class Post(models.Model):
   TOPIC_CHOICES = (
      ('python', '파이썬'), ('c', 'C'), ('comp_arc','컴퓨터구조'),
      ('os', '운영체제'), ('ds', '데이타구조'), ('LD', '논리설계'),
      ('algo', '알고리즘'), ('java','자바'), ('database', '데이타베이스'),
      ('compiler', '컴파일러'), ('oodp', '객체지향'), ('elec_circuit', '전자회로'),
      ('circuit_theory', '회로이론'), ('etc', '기타')
   )
   user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="post_relation")
   tutor = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
   topic = models.CharField(choices=TOPIC_CHOICES, max_length=200, default='etc')
   title = models.CharField(max_length=200)
   content = models.TextField()
   finding_match = models.NullBooleanField(default=True)
   pub_date = models.DateTimeField(auto_now_add=True)
   cancel_reason = models.TextField(null=True)

   def __str__(self):
      return self.get_topic_display() + ' ' + self.title

class Comment(models.Model):
   user = models.ForeignKey(User, on_delete=models.CASCADE)
   post = models.ForeignKey(Post, on_delete=models.CASCADE)
   pub_date = models.DateTimeField(auto_now_add=True)
   content = models.TextField()

class Report(models.Model):
   tutor = models.ForeignKey(User, on_delete=models.CASCADE, related_name="tutor")
   tutee = models.ForeignKey(User, on_delete=models.CASCADE, related_name="tutee")
   post = models.OneToOneField(Post, on_delete=models.CASCADE, related_name="report")
   meeting_date = models.DateTimeField()
   meeting_duration_time = models.PositiveIntegerField(default=0)
   pub_date = models.DateField(auto_now_add=True)
   tutee_feedback = models.TextField(null=True)
   is_confirmed = models.NullBooleanField(default=False)
   content = models.TextField()

   def __str__(self):
      return self.post.get_topic_display() + ' ' + self.post.title
   
   def get_absolute_url(self):
      return reverse('matching:report_detail', args=[self.pk])
