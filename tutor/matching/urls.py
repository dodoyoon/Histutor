from django.urls import path
from . import views

app_name = 'matching'
urlpatterns = [
  path('', views.IndexView.as_view(), name='index'),
<<<<<<< HEAD
  path('tutorReport/', views.tutorReport, name='tutorReport'),
  path('post/new', views.post_new, name='post_new'),
]
=======
  path('signup/', views.signup , name='signup'),
  path('tutorReport/', views.tutorReport, name='tutorReport'),
  path('post/new', views.post_new, name='post_new'),
]
 
>>>>>>> 8fc4fb73b74c49c4d3543be6aec6020600369c14
