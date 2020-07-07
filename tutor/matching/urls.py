from django.urls import path
from . import views

app_name = 'matching'
urlpatterns = [
  path('', views.IndexView.as_view(), name='index'),
  path('tutorReport/', views.tutorReport, name='tutorReport'),
  path('post/new', views.post_new, name='post_new'),
]
 
