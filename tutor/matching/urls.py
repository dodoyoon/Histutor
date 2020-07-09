from django.urls import path
from . import views

app_name = 'matching'
urlpatterns = [
  path('', views.IndexView.as_view(), name='index'),
  path('<int:pk>/profile/', views.save_profile , name='profile'),
  path('userCheck', views.user_check , name='user_check'),
  path('tutorReport/', views.tutorReport, name='tutorReport'),
  path('post/new', views.post_new, name='post_new'),
]
 
