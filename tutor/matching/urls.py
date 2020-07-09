from django.urls import path
from django.conf.urls import url
from . import views

app_name = 'matching'
urlpatterns = [

  path('', views.IndexView.as_view(), name='index'),
  path('<int:pk>/profile/', views.save_profile , name='profile'),
  path('userCheck', views.user_check , name='user_check'),
  path('tutorReport/', views.tutorReport, name='tutorReport'),
  path('post/new/', views.post_new, name='post_new'),
  path('post/detail/<int:pk>/', views.post_detail, name='post_detail'),
  path('tutorHome/', views.tutor_home, name='tutor_home'),
]
