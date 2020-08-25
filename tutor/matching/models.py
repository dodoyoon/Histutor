from django.db import models
from django import forms
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.urls import reverse
from django.db.models import Count


class Profile(models.Model):
   user = models.OneToOneField(User, on_delete=models.CASCADE)
   #nickname = models.CharField(default="", max_length=200, unique=True)
   nickname = models.CharField(default="", max_length=200)
   phone = models.CharField(default="",max_length=200)
   is_tutor = models.BooleanField(null=True,blank=True, default=False)
   signin = models.BooleanField(default=False)
   tutor_tutoringTime = models.PositiveIntegerField(default=0)


   def __str__(self):
      return self.user.username + ' ' + self.user.last_name

   @receiver(post_save, sender=User)
   def create_user_profile(sender, instance, created, **kwargs):
      if created:
         Profile.objects.create(user=instance)

   @receiver(post_save, sender=User)
   def save_user_profile(sender, instance, **kwargs):
      instance.profile.save()

TOPIC_CHOICES = (
      ('python', '파이썬'), ('c', 'C'), ('comp_arc','컴퓨터구조'),
      ('os', '운영체제'), ('ds', '데이타구조'), ('LD', '논리설계'),
      ('algo', '알고리즘'), ('java','자바'), ('database', '데이타베이스'),
      ('compiler', '컴파일러'), ('oodp', '객체지향'), ('elec_circuit', '전자회로'),
      ('circuit_theory', '회로이론'), ('etc', '기타')
)

class Post(models.Model):
   user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="post_relation")
   tutor = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
   topic = models.CharField(choices=TOPIC_CHOICES, max_length=200, default='etc')
   title = models.CharField(max_length=200)
   finding_match = models.BooleanField(null=True,default=True)
   pub_date = models.DateTimeField(auto_now_add=True)
   cancel_reason = models.TextField(null=True)
   start_time = models.DateTimeField(null=True)
   fin_time = models.DateTimeField(null=True)
   hit = models.PositiveIntegerField(default=0)

   @property
   def update_hit(self):
      self.hit += 1
      self.save()

   def __str__(self):
      return self.get_topic_display() + ' ' + self.title

SESSION_TYPE = (
      ('online', '온라인'), ('offline', '오프라인'), ('onoff','온/오프라인'),
)
class TutorSession(models.Model):
   tutor = models.ForeignKey(User, on_delete=models.CASCADE, null=True, related_name='ses')
   title = models.CharField(max_length=300)
   session_type = models.CharField(choices=SESSION_TYPE, default='onoff', max_length=10)
   pub_date = models.DateTimeField(auto_now_add=True)
   start_time = models.DateTimeField(null=True)
   fin_time = models.DateTimeField(null=True)
   hit = models.PositiveIntegerField(default=0)
   location = models.CharField(max_length=500, null=True)

   @property
   def update_hit(self):
      self.hit += 1
      self.save()

   def __str__(self):
      return self.get_session_type_display() + ' ' + self.title

class Comment(models.Model):
   user = models.ForeignKey(User, on_delete=models.CASCADE)
   post = models.ForeignKey(Post, on_delete=models.CASCADE, null=True)
   tutorsession = models.ForeignKey(TutorSession, on_delete=models.CASCADE, null=True)
   pub_date = models.DateTimeField() #TODO auto_now_add=True 로 바꾸기
   content = models.TextField()

   def __str__(self):
      return self.post.title + '    '+self.user.profile.nickname + '    ' + str(self.pub_date)

TIME_CHOICES = (
   (10, 10),
   (20, 20),
   (30, 30),
   (40, 40),
   (50, 50),
   (60, 60),
)

class Report(models.Model):
   tutor = models.ForeignKey(User, on_delete=models.CASCADE, related_name="tutor")
   tutee = models.ForeignKey(User, on_delete=models.CASCADE, related_name="tutee")
   writer = models.ForeignKey(User, on_delete=models.CASCADE, related_name="writer", null=True)
   post = models.OneToOneField(Post, on_delete=models.CASCADE, related_name="report")
   pub_date = models.DateField(auto_now_add=True)
   is_confirmed = models.BooleanField(null=True,default=False)
   content = models.TextField()
   join_tutee = models.TextField(null=True)
   duration_time = models.PositiveIntegerField(choices=TIME_CHOICES, default=10)

   def __str__(self):
      return self.post.get_topic_display() + ' ' + self.post.title

   def get_absolute_url(self):
      return reverse('matching:report_detail', args=[self.pk])



class SessionLog(models.Model):
   tutor_session = models.ForeignKey(TutorSession, on_delete=models.CASCADE, related_name="tutor_session")
   tutee = models.ForeignKey(User, on_delete=models.CASCADE, related_name="log_tutee")
   is_waiting = models.BooleanField(default=True)
   wait_time = models.DateTimeField(auto_now_add=True)
   start_time = models.DateTimeField(null=True)
   fin_time = models.DateTimeField(null=True)

   def ranking(self):
    waitingList = SessionLog.objects.filter(is_waiting=True, wait_time__lt=self.wait_time).aggregate(ranking=Count('wait_time'))
    return waitingList['ranking'] + 1
   def __str__(self):
      return self.tutee.profile.nickname +' ' + str(self.is_waiting) +' ' + str(self.wait_time) + ' ' + self.tutor_session.title
