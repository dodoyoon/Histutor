from django.urls import path
from django.conf.urls import url
from . import views

app_name = 'matching'
urlpatterns = [
  path('', views.index, name='index'),
  path('tutee_home/', views.tutee_home, name='tutee_home'),
  path('signup/', views.signup , name='signup'),
  path('tutorReport/', views.tutorReport, name='tutorReport'),
  path('post/new/', views.post_new, name='post_new'),
  path('post/detail/<int:pk>/', views.post_detail, name='post_detail'),
  path('tutorHome/', views.tutor_home, name='tutor_home'),
]
