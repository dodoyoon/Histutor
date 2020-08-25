from django.urls import path
from django.conf.urls import url
from . import views

app_name = 'matching'
urlpatterns = [

  path('', views.index, name='index'),
  path('<int:pk>/profile/', views.save_profile , name='profile'),
  path('userCheck/', views.user_check , name='user_check'),
  path('post/new/', views.post_new, name='post_new'),
  path('post/detail/<int:pk>/', views.post_detail, name='post_detail'),
  path('post/edit/<int:pk>/', views.post_edit, name='post_edit'),
  path('mypage/', views.mypage, name='mypage'),
  path('mypage/post/', views.mypage_post, name='mypage_post'),
  path('mypage/report/', views.mypage_report, name='mypage_report'),
  path('mypage/tutor_post/', views.mypage_tutor_post, name='mypage_tutor_post'),
  path('post/detail/close_post/<int:pk>', views.close_post, name='close_post'),
  path('post/detail/fin_tutoring/<int:pk>', views.fin_tutoring, name='fin_tutoring'),
  path('post/detail/cancel_tutoring/<int:pk>', views.cancel_tutoring, name='cancel_tutoring'),
  path('post/settutor/<int:postpk>/<int:userpk>/', views.set_tutor, name='set_tutor'),
  path('tutor/detail/<int:pk>', views.tutor_detail, name='tutor_detail'),
  path('tutee/detail/<int:pk>', views.tutee_detail, name='tutee_detail'),
  path('login/', views.login, name='login'),
  path('admin/tutor-list', views.admin_home, name='admin_home'),
  path('admin/tutee-list/', views.tutee_list, name='tutee_list'),
  path('admin/list', views.userlist, name='userlist'),
  path('admin/make-tutor/<int:pk>', views.make_tutor, name='make_tutor'),
  path('admin/remove-tutor/<int:pk>', views.remove_tutor, name='remove_tutor'),
  path('send_message/', views.send_message, name='send_message'),
  path('report/<int:pk>/', views.tutee_report, name='tutee_report'),
  path('report/detail/<int:pk>/', views.ReportDetail.as_view(), name='report_detail'),
  # path('report/edit/<int:pk>/', views.ReportUpdate.as_view(), name='report_update'),
  #path('', views.index, name='index'),
  #path('<str:room_name>/', views.room, name='room'),
  path('main/', views.mainpage, name='mainpage'),
]
