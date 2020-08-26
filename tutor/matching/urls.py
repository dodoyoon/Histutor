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
  path('session/detail/<int:pk>/', views.session_detail, name='session_detail'),
  path('session/report/create/<int:pk>/', views.session_report_create, name='session_report_create'),
  path('session/detail/<int:pk>/waitingroom/', views.waitingroom, name='waitingroom'),
  path('session/detail/end_session/<int:pk>', views.end_session, name='end_session'),
  url(r'^not_waiting/$', views.not_waiting, name='not_waiting'),
  url(r'^set_attending_type/$', views.set_attending_type, name='set_attending_type'),
  path('mypage/', views.mypage, name='mypage'),
  path('mypage/post/', views.mypage_post, name='mypage_post'),
  path('mypage/tutor-session/', views.mypage_session, name='mypage_tutor_session'),
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
  path('report/list/<int:pk>/', views.report_list, name='report_list'),
  path('report/detail/<int:pk>/', views.ReportDetail.as_view(), name='report_detail'),
  # path('report/edit/<int:pk>/', views.ReportUpdate.as_view(), name='report_update'),
  #path('', views.index, name='index'),
  #path('<str:room_name>/', views.room, name='room'),
  path('main/', views.mainpage, name='mainpage'),
  #path('post/detail/<int:pk>/waiting/', views.waitingpage, name='waiting_room')
  # path('post/detail/waiting/', views.waitingroom, name='waiting_room')
]
