from django.urls import path
from django.conf.urls import url
from . import views

app_name = 'matching'
urlpatterns = [

  path('', views.index, name='index'),
  path('<int:pk>/profile/', views.save_profile , name='profile'),
  path('userCheck/', views.user_check , name='user_check'),
  path('report/<int:pk>/', views.tutor_report, name='tutor_report'),
  path('report/detail/<int:pk>/', views.report_detail, name='report_detail'),
  path('post/new/', views.post_new, name='post_new'),
  path('post/detail/<int:pk>/', views.post_detail, name='post_detail'),
  path('post/edit/<int:pk>/', views.post_edit, name='post_edit'),
  path('mypage/', views.mypage, name='mypage'),
  path('mypage/post/', views.mypage_post, name='mypage_post'),
  path('mypage/report/', views.mypage_report, name='mypage_report'),
  path('mypage/incomplete/', views.mypage_incomplete, name='mypage_incomplete'),
  path('tutor_home/', views.tutor_home, name='tutor_home'),
  path('tutee_home/', views.tutee_home, name='tutee_home'),
  path('post/detail/close_post/<int:pk>', views.close_post, name='close_post'),
  path('post/settutor/<int:postpk>/<int:userpk>/', views.set_tutor, name='set_tutor'),
  path('login/', views.login, name='login'),
  path('admin_home/', views.admin_home, name='admin_home'),
  #path('', views.index, name='index'),
  #path('<str:room_name>/', views.room, name='room'),
]
