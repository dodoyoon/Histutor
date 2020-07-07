from django.urls import path
from . import views

app_name = 'matching'
urlpatterns = [
  path('', views.IndexView.as_view(), name='index'),
<<<<<<< HEAD
  path('tutorReport/', views.tutorReport, name='tutorReport'),
]
=======
  path('post/new', views.post_new, name='post_new'),
]
>>>>>>> 1ed0f3e11cc887ac0dfc2727b5a9770ac67e5cf6
