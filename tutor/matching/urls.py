from django.urls import path
from django.conf.urls import url
from . import views

app_name = 'matching'
urlpatterns = [

  path('', views.index, name='index'),
  path('<int:pk>/profile/', views.save_profile , name='profile'),
  path('userCheck/', views.user_check , name='user_check'),
  path('tutor_report/', views.tutor_report, name='tutor_report'),
  path('post/new/', views.post_new, name='post_new'),
  path('post/detail/<int:pk>/', views.post_detail, name='post_detail'),
  path('post/edit/<int:pk>/', views.post_edit, name='post_edit'),
  path('tutee/mypage/', views.tutee_mypage, name='tutee_mypage'),
  path('tutor_home/', views.tutor_home, name='tutor_home'),
  path('tutee_home/', views.tutee_home, name='tutee_home'),
  path('tutee_accept_report/', views.tutee_accept_report, name='tutee_accept_report'),
  path('login/', views.login, name='login'),
  path('admin_home/', views.admin_home, name='admin_home'),
]
