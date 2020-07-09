from django.urls import path
from . import views

app_name = 'matching'
urlpatterns = [
  path('', views.index, name='index'),
  path('tutee_home/', views.tutee_home, name='tutee_home'),
  path('signup/', views.signup , name='signup'),
  path('tutorReport/', views.tutorReport, name='tutorReport'),
  path('post/new/', views.post_new, name='post_new'),
  path('tutorHome/', views.tutor_home, name='tutor_home'),
]
 
