from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.db.models import F, Q, Count
from django.views import generic
from django.contrib.auth.models import User
from .forms import PostForm, CommentForm, AcceptReportForm, AccuseForm, ReportForm, TutorReportForm, TutorSessionForm
from django.contrib.auth.decorators import login_required
from matching import models as matching_models
from django.db import transaction
from itertools import chain
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from matching.models import TOPIC_CHOICES
import json
from django.core.serializers.json import DjangoJSONEncoder
from django.views.generic.edit import UpdateView
from django.views.generic.detail import DetailView
from .models import Report
from django.utils import timezone
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required

URL_LOGIN = "/matching"
# DEFAULT PAGE

def index(request):
    if request.user.is_authenticated:
        return redirect('matching:mainpage')
    else:
        return redirect('login/')

def login(request):
    return render(request, 'matching/account_login.html', {})

def redirect_to_main(request):
    return redirect('matching:mainpage')


@login_required(login_url=URL_LOGIN)
@transaction.atomic
def save_profile(request, pk):
    user = matching_models.User.objects.get(pk=pk)
    if not request.user.is_authenticated:
        return redirect('/accounts/login/')
    if request.method == 'POST':
        profile = user.profile
        profile.signin = True
        profile.phone = "010" + str(request.POST['phone1']) + str(request.POST['phone2'])
        profile.save()
        return redirect(reverse('matching:mainpage'))
    print("nickname : ", user.profile.nickname)
    return render(request, 'matching/save_profile.html', {'nickname': user.profile.nickname})

def user_check(request):
    if request.user.email.endswith('@handong.edu'):
        try:
            user = matching_models.User.objects.get(pk=request.user.pk)
            if user.profile.signin == False:
                user.profile.nickname =user.username[1:3] + user.last_name
                user.profile.signin = True
                user.profile.save()
                return HttpResponseRedirect(reverse('matching:profile', args=(request.user.pk,)))
            else:
                return HttpResponseRedirect(reverse('matching:mainpage'))
        except(KeyError, matching_models.User.DoesNotExist):
            return HttpResponseRedirect(reverse('matching:index'))
    else:
        messages.info(request, '한동 이메일로 로그인해주세요.')
        matching_models.User.objects.filter(pk=request.user.pk).delete()
        return HttpResponseRedirect(reverse('matching:index'))

# #TODO : method decorator should be added
# class ReportUpdate(UpdateView):
#     model = Report
#     context_object_name = 'report'
#     form_class = ReportForm
#     template_name = 'matching/report_edit.html'


@login_required(login_url=URL_LOGIN)
def tutee_report(request, pk):
    post = matching_models.Post.objects.get(pk=pk)
    if not (post.user == request.user or post.tutor == request.user):
        return redirect('matching:post_detail', pk=pk)

    report = matching_models.Report.objects.filter(post=pk, writer=request.user)
    if report.exists():
        return redirect('matching:post_detail', pk=pk)

    if request.method == "POST":
        if post.user == post.tutor:
            form = TutorReportForm(request.POST)
        else:
            form = ReportForm(request.POST)
        

        if form.is_valid():
            report = form.save(commit=False)
            if post.fin_time is None:
                fin_tutoring(request,pk)
            report.tutor = matching_models.User.objects.get(pk = post.tutor.pk)
            report.tutee = matching_models.User.objects.get(pk = post.user.pk)
            report.post = post
            report.writer = request.user
            report.save()
            profile = matching_models.Profile.objects.get(user = report.tutor)
            profile.tutor_tutoringTime += form.cleaned_data['duration_time']
            profile.save()
            return redirect('matching:report_detail', pk=report.pk)
        else:
            return redirect('matching:mainpage')

class ReportDetail(DetailView):
    model = Report

    def get(self, request, *args, **kwargs):
        report = matching_models.Report.objects.get(pk=self.kwargs['pk'])
        if self.request.user.is_staff or self.request.user == report.post.user:
            return super(ReportDetail, self).get(request, *args, **kwargs)
        else:
            return redirect('matching:mainpage')

    def get_context_data(self, **kwargs):
        context = super(ReportDetail, self).get_context_data(**kwargs)
        context['form'] = AccuseForm
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = AccuseForm(request.POST, request.FILES)

        if form.is_valid():
            return self.form_valid(form, self.object)

    def form_valid(self, form, report):
        report.tutee_feedback = form.cleaned_data['tutee_feedback']
        report.save()

def report_list(request, pk):
    post = matching_models.Post.objects.get(pk=pk)
    report_list = matching_models.Report.objects.filter(post=post)
    tutor_report = matching_models.Report.objects.filter(writer=post.tutor)
    tutee_report = matching_models.Report.objects.filter(writer=post.user)

    ctx = {
        'post' : post,
        'report_list' : report_list,
        'tutor_report' : tutor_report,
        'tutee_report' : tutee_report,
    }

    return render(request, 'matching/report_list.html', ctx)


@login_required(login_url=URL_LOGIN)
def post_new(request):
    if request.method == "POST":
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            user_obj = matching_models.User.objects.get(username=request.user.username)
            post.user = user_obj
            post.pub_date = timezone.localtime()
            post.finding_match = True
            post.save()



            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                'new_post',
                {
                    'type': 'new_post',
                    'id': post.pk,
                    'title': post.title,
                    'finding': post.finding_match,
                    'pub_date': json.dumps(post.pub_date, cls=DjangoJSONEncoder),
                    #'topic': dict(TOPIC_CHOICES).get(post.topic),
                    'nickname': post.user.profile.nickname,
                }
            )

            return redirect('matching:post_detail', pk=post.pk)
    else:
        form = PostForm()


    ctx['form'] = form

    return render(request, 'matching/post_new.html', ctx)


@login_required(login_url=URL_LOGIN)
def post_detail(request, pk):
    ctx={}

    try:
        post = get_object_or_404(matching_models.Post, pk=pk)
    except matching_models.Post.DoesNotExist:
        return HttpResponse("게시물이 존재하지 않습니다.")
    except:
        messages.error(request, '해당 방은 존재하지 않습니다.')
        return HttpResponseRedirect(reverse('matching:mainpage'))

    user = matching_models.User.objects.get(username=request.user.username)
    post = matching_models.Post.objects.get(pk=pk)
    my_report = matching_models.Report.objects.filter(writer=user, post=pk)
    
    if my_report.exists(): #사용자가 쓴 보고서 존재 
        ctx['my_report'] = my_report
        ctx['my_report_pk'] = my_report[0].pk
    elif post.fin_time or ((request.user == post.user) and post.tutor): 
        #사용자가 쓴 보고서 존재하지 않고 종료되었거나 
        if post.tutor == post.user:
            report_form = TutorReportForm()
        else:
            report_form = ReportForm()
        ctx['report_form'] = report_form
        ctx['report_post_pk'] = post.pk
        ctx['report_exist'] = True
    else:
        print("else")

    comment_list = matching_models.Comment.objects.filter(post=post).order_by('pub_date')

    ctx['post'] = post
    ctx['comment_list'] = comment_list
    ctx['start_msg'] = "튜터링시작"+post.user.last_name+str(post.pub_date)
    ctx['cancel_msg'] = "튜터링취소"+post.user.last_name+str(post.pub_date)
    
    post.hit = post.hit + 1
    post.save()
    return render(request, 'matching/post_detail.html', ctx)



def set_tutor(request, postpk, userpk):
    post = matching_models.Post.objects.filter(tutor=request.user, fin_time__isnull=True)
    if post:
        # 튜터가 하나 이상의 튜터링을 동시에 진행할 수 없음
        return redirect('matching:post_detail', pk=postpk)

    try:
        post = get_object_or_404(matching_models.Post, pk=postpk)
    except post.DoesNotExist:
        return HttpResponse("포스트가 없습니다.")

    try:
        tutor = get_object_or_404(User, pk=userpk)
    except tutor.DoesNotExist:
        return HttpResponse("사용자가 없습니다.")

    # if tutor.pk == post.user.pk:
    #     #포스트 작성자가 직접 튜터가 될 수 없음.
    #     return redirect('matching:post_detail', pk=post.pk)

    if post.tutor:
        messages.error(request, '해당 방은 튜터링이 이미 진행중입니다.')
        return HttpResponseRedirect(reverse('matching:mainpage'))


    post.tutor = tutor
    post.finding_match = False
    post.start_time = timezone.localtime()
    post.save()

    start_tutoring_cmt = matching_models.Comment(user=tutor, post=post, pub_date=post.start_time, content="튜터링시작"+post.user.last_name+str(post.pub_date))
    start_tutoring_cmt.save()

    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
      'new_comment',
      {
        'type': 'star_comment',
        'id': start_tutoring_cmt.pk,
      }
  )

    return redirect('matching:post_detail', pk=post.pk)

@login_required
def send_message(request):
    if request.method == "GET":
        post = matching_models.Post.objects.get(pk=request.GET['postid'])
        if post.finding_match or request.user == post.tutor or request.user == post.user:
            new_cmt = matching_models.Comment(user=request.user, post=post, pub_date=timezone.localtime(), content=request.GET['content'])
            new_cmt.save()
            return HttpResponse(new_cmt.id)
        else:
            messages.error(request, '해당 방은 튜터링이 시작되었습니다.')
            return HttpResponseRedirect(reverse('matching:mainpage'))
    else:
        return HttpResponse('NOT A GET REQUEST')



@login_required(login_url=URL_LOGIN)
def post_edit(request, pk):
    ctx={}
    post = matching_models.Post.objects.get(pk=pk)

    if post.user.pk != request.user.pk:
        return redirect('matching:post_detail', pk=post.pk)

    form = PostForm(request.POST)
    if request.method == "POST":
        if form.is_valid():
            #post.topic = form.cleaned_data['topic']
            post.title = form.cleaned_data['title']
            post.save()
            return redirect('matching:post_detail', pk=post.pk)
    else:
        ctx['post'] = post

    return render(request, 'matching/post_edit.html', ctx)




@login_required(login_url=URL_LOGIN)
@staff_member_required
def admin_home(request):
    tutorlist = matching_models.User.objects.filter(profile__is_tutor=True).order_by('-profile__tutor_tutoringTime')

    ctx = {
        'tutorlist': tutorlist,
    }

    return render(request, 'matching/admin_tutor_list.html', ctx)

@login_required(login_url=URL_LOGIN)
@staff_member_required
def tutee_list(request):
    
    tutee_list = matching_models.User.objects.filter(profile__is_tutor=False).annotate(
        num_posts = Count('post_relation')
    )

    ctx = {
        'tutee_list': tutee_list,
    }
    return render(request, 'matching/admin_tutee_list.html', ctx)

@staff_member_required
def userlist(request):
    search_word = request.GET.get('search_word', '')
    if search_word != '':
        userlist = matching_models.User.objects.filter(Q(profile__nickname__icontains=search_word) | Q(email__icontains=search_word))
    else:
        userlist = matching_models.User.objects.all()

    ctx = {
        'userlist': userlist,
    }

    if search_word != '':
        ctx['search_word'] = search_word

    return render(request, 'matching/admin_user_list.html', ctx)

@staff_member_required
def make_tutor(request, pk):
    user = matching_models.User.objects.get(pk=pk)
    userinfo = matching_models.Profile.objects.get(user=user)
    userinfo.is_tutor = True
    userinfo.save()

    return redirect(reverse('matching:userlist'))

@staff_member_required
def remove_tutor(request, pk):
    user = matching_models.User.objects.get(pk=pk)
    userinfo = matching_models.Profile.objects.get(user=user)
    userinfo.is_tutor = False
    userinfo.save()

    return redirect(reverse('matching:userlist'))


@login_required(login_url=URL_LOGIN)
def tutor_detail(request, pk):
    if not request.user.is_staff:
        return redirect(reverse('matching:mainpage'))

    tutor = matching_models.User.objects.get(pk=pk)
    postlist = matching_models.Post.objects.filter(tutor=tutor)

    ctx = {
        'tutor' : tutor,
        'postlist' : postlist,
    }

    return render(request, 'matching/tutor_detail.html', ctx)

@login_required(login_url=URL_LOGIN)
def tutee_detail(request, pk):
    if not request.user.is_staff:
        return redirect(reverse('matching:mainpage'))

    tutee = matching_models.User.objects.get(pk=pk)
    postlist = matching_models.Post.objects.filter(user=tutee)

    ctx = {
        'tutee' : tutee,
        'postlist' : postlist,
    }

    return render(request, 'matching/tutee_detail.html', ctx)

# Tutee가 끝낼 때
def close_post(request, pk):
    post = matching_models.Post.objects.get(pk=pk)
    post.finding_match = False
    post.save()
    return redirect(reverse('matching:mainpage'))

# Tutor가 끝낼 때
def fin_tutoring(request, pk):
    post = matching_models.Post.objects.get(pk=pk)
    post.fin_time = timezone.localtime()
    post.save()
    return redirect(reverse('matching:mainpage'))

# Tutor가 튜터링 중도 취소
def cancel_tutoring(request, pk):
    post = matching_models.Post.objects.get(pk=pk)

    cancel_tutoring_cmt = matching_models.Comment(user=post.tutor, post=post, pub_date=timezone.localtime(), content="튜터링취소"+post.user.last_name+str(post.pub_date))
    cancel_tutoring_cmt.save()

    post.tutor = None
    post.finding_match = True
    post.start_time = None
    post.save()


    return redirect(reverse('matching:mainpage'))



@login_required(login_url=URL_LOGIN)
def mypage(request):
    ctx = {}
    return redirect(reverse('matching:mypage_post'))


@login_required(login_url=URL_LOGIN)
def mypage_post(request):
    ctx = {}
    post = matching_models.Post.objects.filter(user=request.user)

    recruiting = post.filter(finding_match = True).order_by('-pub_date')
    onprocess = post.filter(start_time__isnull = False, fin_time__isnull = True).order_by('-pub_date')
    recruited = post.filter(finding_match = False).order_by('-pub_date')
    recruited = recruited.exclude(start_time__isnull = False, fin_time__isnull = True)
    #posts = tutor_models.Post.objects.order_by('-pub_date')
    posts = list(chain(recruiting, onprocess, recruited))

    current_post_page = request.GET.get('page', 1)

    post_paginator = Paginator(posts, 10)
    try:
        posts = post_paginator.page(current_post_page)
    except PageNotAnInteger:
        posts = post_paginator.page(1)
    except EmptyPage:
        posts = post_paginator.page(post_paginator.num_pages)

    neighbors = 10
    if post_paginator.num_pages > 2*neighbors:
        start_index = max(1, int(current_post_page)-neighbors)
        end_index = min(int(current_post_page)+neighbors, post_paginator.num_pages)
        if end_index < start_index + 2*neighbors:
            end_index = start_index + 2*neighbors
        elif start_index > end_index - 2*neighbors:
            start_index = end_index - 2*neighbors
        if start_index < 1:
            end_index -= start_index
            start_index = 1
        elif end_index > post_paginator.num_pages:
            start_index -= end_index - post_paginator.num_pages
            end_index = post_paginator.num_pages
        paginatorRange = [f for f in range(start_index, end_index+1)]
        paginatorRange[:(2*neighbors + 1)]
    else:
        paginatorRange = range(1, post_paginator.num_pages+1)

    ctx = {
        'posts' : posts,
        'postPaginator': post_paginator,
        'paginatorRange': paginatorRange,
    }
    return render(request, 'matching/mypage_post.html', ctx)



@login_required(login_url=URL_LOGIN)
def mypage_report(request):
    ctx = {}

    # tutee = matching_models.User.objects.get(pk=request.user.pk)
    report = matching_models.Report.objects.filter(tutee=request.user).order_by('-pub_date')

    current_report_page = request.GET.get('page', 1)

    report_paginator = Paginator(report, 10)
    try:
        reports = report_paginator.page(current_report_page)
    except PageNotAnInteger:
        reports = report_paginator.page(1)
    except EmptyPage:
        reports = report_paginator.page(report_paginator.num_pages)

    neighbors = 10
    if report_paginator.num_pages > 2*neighbors:
        start_index = max(1, int(current_report_page)-neighbors)
        end_index = min(int(current_report_page)+neighbors, report_paginator.num_pages)
        if end_index < start_index + 2*neighbors:
            end_index = start_index + 2*neighbors
        elif start_index > end_index - 2*neighbors:
            start_index = end_index - 2*neighbors
        if start_index < 1:
            end_index -= start_index
            start_index = 1
        elif end_index > report_paginator.num_pages:
            start_index -= end_index - report_paginator.num_pages
            end_index = report_paginator.num_pages
        paginatorRange = [f for f in range(start_index, end_index+1)]
        paginatorRange[:(2*neighbors + 1)]
    else:
        paginatorRange = range(1, report_paginator.num_pages+1)

    ctx = {
        'reports': reports,
        'reportPaginator': report_paginator,
        'paginatorRange': paginatorRange,
    }

    return render(request, 'matching/mypage_report.html', ctx)


@login_required(login_url=URL_LOGIN)
def mypage_tutor_post(request):
    ctx = {}
    post = matching_models.Post.objects.filter(tutor=request.user)

    recruiting = post.filter(finding_match = True).order_by('-pub_date')
    onprocess = post.filter(start_time__isnull = False, fin_time__isnull = True).order_by('-pub_date')
    recruited = post.filter(finding_match = False).order_by('-pub_date')
    recruited = recruited.exclude(start_time__isnull = False, fin_time__isnull = True)
    #posts = tutor_models.Post.objects.order_by('-pub_date')
    posts = list(chain(recruiting, onprocess, recruited))

    current_post_page = request.GET.get('page', 1)

    post_paginator = Paginator(posts, 10)
    try:
        posts = post_paginator.page(current_post_page)
    except PageNotAnInteger:
        posts = post_paginator.page(1)
    except EmptyPage:
        posts = post_paginator.page(post_paginator.num_pages)

    neighbors = 10
    if post_paginator.num_pages > 2*neighbors:
        start_index = max(1, int(current_post_page)-neighbors)
        end_index = min(int(current_post_page)+neighbors, post_paginator.num_pages)
        if end_index < start_index + 2*neighbors:
            end_index = start_index + 2*neighbors
        elif start_index > end_index - 2*neighbors:
            start_index = end_index - 2*neighbors
        if start_index < 1:
            end_index -= start_index
            start_index = 1
        elif end_index > post_paginator.num_pages:
            start_index -= end_index - post_paginator.num_pages
            end_index = post_paginator.num_pages
        paginatorRange = [f for f in range(start_index, end_index+1)]
        paginatorRange[:(2*neighbors + 1)]
    else:
        paginatorRange = range(1, post_paginator.num_pages+1)

    ctx = {
        'posts' : posts,
        'postPaginator': post_paginator,
        'paginatorRange': paginatorRange,
    }
    return render(request, 'matching/mypage_tutor_post.html', ctx)

import requests
@login_required(login_url=URL_LOGIN)
def mainpage(request):
    post = matching_models.Post.objects.filter(user = request.user, finding_match = True)
    post_exist = False

    if post:
        post_exist = True

    user = matching_models.User.objects.get(pk=request.user.pk)

    ongoing_tutoring = matching_models.Post.objects.filter(tutor=user).filter(fin_time__isnull=True)
    if ongoing_tutoring.exists():
        ongoing_tutoring = ongoing_tutoring[:1].get()

    ongoing_post = matching_models.Post.objects.filter(user=user).filter(finding_match=True)
    if ongoing_post.exists():
        ongoing_post = ongoing_post[:1].get()

    if request.method == "POST":
        tsform = TutorSessionForm(request.POST)
        form = PostForm(request.POST)
        check_post_exist = matching_models.Post.objects.filter(user = request.user, finding_match = True)

        if tsform.is_valid():
            tutorsession = tsform.save(commit=False)
            user_obj = matching_models.User.objects.get(username=request.user.username)
            tutorsession.tutor = user_obj
            tutorsession.pub_date = timezone.localtime()
            tutorsession.save()

            '''
            try:
            post.report.exists()
            reportExist = True
            except:
            reportExist = False

            try:
            post.tutor.exists()
            tutorExist = True
            except:
            tutorExist = False
            '''

            return redirect('matching:session_detail', pk=tutorsession.pk)

        elif form.is_valid() and not check_post_exist:
            post = form.save(commit=False)
            user_obj = matching_models.User.objects.get(username=request.user.username)
            post.user = user_obj
            post.pub_date = timezone.localtime()
            post.finding_match = True
            post.save()

            try:
              post.report.exists()
              reportExist = True
            except:
              reportExist = False

            try:
              post.tutor.exists()
              tutorExist = True
            except:
              tutorExist = False

            '''
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                'new_post',
                {
                    'type': 'new_post',
                    'id': post.pk,
                    'title': post.title,
                    'finding': post.finding_match,
                    'pub_date': json.dumps(post.pub_date, cls=DjangoJSONEncoder),
                    #'topic': dict(TOPIC_CHOICES).get(post.topic),
                    'nickname': post.user.profile.nickname,
                    'startTime': json.dumps(post.start_time, cls=DjangoJSONEncoder),
                    'endTime': json.dumps(post.fin_time, cls=DjangoJSONEncoder),
                    'postUser': post.user.pk,
                    'tutor': tutorExist,
                    'reportExist': reportExist,
                    'hit': post.hit,
                }
            )
            '''
            title = post.title
            url = "http://" + request.get_host() + reverse('matching:post_detail', args=[post.pk])
            payload = '{"body":"' + title + '","connectColor":"#6C639C","connectInfo":[{"imageUrl":"' + url + '"}]}'

            headers = {'Accept': 'application/vnd.tosslab.jandi-v2+json',
            'Content-Type': 'application/json'}

            #r = requests.post("https://wh.jandi.com/connect-api/webhook/20949533/4bbee5c811038e410ccea15513acd716", data=payload.encode('utf-8'), headers=headers)
            return redirect('matching:post_detail', pk=post.pk)
    else:
        form = PostForm()
        tsform = TutorSessionForm()


    search_word = request.GET.get('search_word', '') # GET request의 인자중에 q 값이 있으면 가져오고, 없으면 빈 문자열 넣기
    now = timezone.localtime()

    tutoring_on = matching_models.TutorSession.objects.filter(start_time__lte=now, fin_time__gte=now)
    tutoring_off = matching_models.TutorSession.objects.filter(fin_time__lte=now)
    recruiting = matching_models.Post.objects.filter(finding_match = True).order_by('-pub_date')
    onprocess = matching_models.Post.objects.filter(start_time__isnull = False, fin_time__isnull = True).order_by('-pub_date')
    recruited = matching_models.Post.objects.filter(finding_match = False, fin_time__isnull = False).order_by('-pub_date')

    ### 튜터링 검색기능 ###
    if search_word != '':
        tutoring_on = tutoring_on.filter(title__icontains=search_word)
        tutoring_off = tutoring_off.filter(title__icontains=search_word)
        recruiting = recruiting.filter(title__icontains=search_word)
        onprocess = onprocess.filter(title__icontains=search_word)
        recruited = recruited.filter(title__icontains=search_word)
        
    posts = list(chain(tutoring_on,recruiting, onprocess,recruited, tutoring_off))

    current_post_page = request.GET.get('page', 1)
    post_paginator = Paginator(posts, 9)
    try:
        posts = post_paginator.page(current_post_page)
    except PageNotAnInteger:
        posts = post_paginator.page(1)
    except EmptyPage:
        posts = post_paginator.page(post_paginator.num_pages)


    print(">>> posts len: " + str(len(posts)))
    neighbors = 10
    if post_paginator.num_pages > 2*neighbors:
        start_index = max(1, int(current_post_page)-neighbors)
        end_index = min(int(current_post_page)+neighbors, post_paginator.num_pages)
        if end_index < start_index + 2*neighbors:
            end_index = start_index + 2*neighbors
        elif start_index > end_index - 2*neighbors:
            start_index = end_index - 2*neighbors
        if start_index < 1:
            end_index -= start_index
            start_index = 1
        elif end_index > post_paginator.num_pages:
            start_index -= end_index - post_paginator.num_pages
            end_index = post_paginator.num_pages
        paginator_range = [f for f in range(start_index, end_index+1)]
        paginator_range[:(2*neighbors + 1)]
    else:
        paginator_range = range(1, post_paginator.num_pages+1)


    ctx = {
        'ongoing_tutoring' : ongoing_tutoring,
        'ongoing_post': ongoing_post,
        'user': user,
        'posts': posts,
        'postPaginator': post_paginator,
        'paginatorRange': paginator_range,
        'form': form,
        'tsform': tsform,
        'post_exist': post_exist,
        'today' : timezone.localtime(),
    }

    # main.html에서 튜티도 진행중인 튜터링이 보이게 하기
    if not user.profile.is_tutor:
        try :
            ongoing_tutoring_tutee = matching_models.Post.objects.get(user=user, tutor__isnull=False, start_time__isnull=False, fin_time__isnull=True)
            ctx['ongoing_tutoring_tutee'] = ongoing_tutoring_tutee
        except matching_models.Post.DoesNotExist :
            ongoing_tutoring_tutee = None


    # Tutor Report Part
    user_obj2 = matching_models.User.objects.get(username=request.user.username)
    report_to_write = matching_models.Post.objects.filter(tutor=user_obj2, tutor__isnull=False).exclude(report__writer=user_obj2)
    if report_to_write.exists():
        for report in report_to_write:
            if report.tutor == report.user:
                report_form = TutorReportForm()
            else:
                report_form = ReportForm()
            ctx['report_form'] = report_form
            ctx['report_post_pk'] = report.pk

            # Tutoring이 정상적으로 종료되었을 경우
            if report.fin_time:
                ctx['report_exist'] = True
                ctx['unwritten_report'] = report

    return render(request, 'matching/main.html', ctx)


def get_next_tutee(request, session, req_user):
    # session log
    if session.tutor != req_user:
        print(str(session.tutor.pk) + " vs " + str(req_user.pk))
        messages.error(request, '해당 튜터만 새로운 튜터링을 시작할 수 있습니다.')
        return HttpResponseRedirect(reverse('matching:mainpage'))
    try:
        next_tutee = matching_models.SessionLog.objects.filter(tutor_session=session, is_waiting=True).earliest('wait_time')
    except matching_models.SessionLog.DoesNotExist:
        next_tutee = None
        
    if next_tutee:
        next_tutee.start_time = timezone.localtime()
        next_tutee.is_waiting = False 
        next_tutee.save()

    return next_tutee

def fin_current_tutee(request, session):
    try:
        current_tutee = matching_models.SessionLog.objects.get(tutor_session=session, is_waiting=False, start_time__isnull=False, fin_time__isnull=True)
        print("Current Tutee", current_tutee)
        current_tutee.fin_time = timezone.localtime()
        current_tutee.save()
    except:
        print("현재 참여중인 튜티가 없습니다.")

@login_required(login_url=URL_LOGIN)
def session_detail(request, pk):
    ctx={}

    try:
        session = get_object_or_404(matching_models.TutorSession, pk=pk)
    except matching_models.TutorSession.DoesNotExist:
        return HttpResponse("게시물이 존재하지 않습니다.")
    except:
        messages.error(request, '해당 튜터세션은 존재하지 않습니다.')
        return HttpResponseRedirect(reverse('matching:mainpage'))

    req_user = matching_models.User.objects.get(username=request.user.username)
    '''report_to_write = matching_models.Post.objects.filter(user=user, pk=pk, report__isnull=True, tutor__isnull=False)

    if report_to_write.exists():
        for report in report_to_write:
            if report.tutor == report.user:
                report_form = TutorReportForm()
            else:
                report_form = ReportForm()
            ctx['report_form'] = report_form
            ctx['report_post_pk'] = report.pk
            ctx['report_exist'] = True'''
    if request.method == 'POST':
        fin_current_tutee(request, session)
        next_tutee = get_next_tutee(request, session, req_user)
        ctx['tutee'] = next_tutee


    comment_list = matching_models.Comment.objects.filter(tutorsession=session).order_by('pub_date')

    ctx['session'] = session
    ctx['comment_list'] = comment_list
    '''ctx['start_msg'] = "튜터링시작"+session.user.last_name+str(session.pub_date)
    ctx['cancel_msg'] = "튜터링취소"+session.user.last_name+str(session.pub_date)
    '''
    session.hit = session.hit + 1
    session.save()
    return render(request, 'matching/session_detail.html', ctx)


@login_required(login_url=URL_LOGIN)
def waitingroom(request, pk):
    user = matching_models.User.objects.get(username=request.user.username)
    if user.profile.is_tutor:
        return redirect('matching:session_detail', pk=pk)

    try:
        session = get_object_or_404(matching_models.TutorSession, pk=pk)
    except matching_models.TutorSession.DoesNotExist:
        return HttpResponse("게시물이 존재하지 않습니다.")
    except:
        messages.error(request, '해당 튜터세션은 존재하지 않습니다.')
        return HttpResponseRedirect(reverse('matching:mainpage'))



    # session log 만들기: session detail에 들어오면 무조건 하나의 log 만들기
    try:
      log = matching_models.SessionLog.objects.get(is_waiting=True, tutee=user)
    except matching_models.SessionLog.DoesNotExist:
      if not user.profile.is_tutor:
        log = matching_models.SessionLog.objects.create(tutor_session=session, tutee=user)
        log.save()
    except:
      messages.error(request, "해당 튜터세션은 존재하지 않습니다.")
      return HttpResponseRedirect(reverse('matching:mainpage'))

    waitingList = matching_models.SessionLog.objects.filter(is_waiting=True)
    waitingTutee = waitingList.get(tutee = request.user) # 에러 뜸
    tuteeTurn = waitingTutee.ranking()
    totalWaiting = len(waitingList)
    if totalWaiting == 1:
      waitingBeforeTutee = 0
      waitingAfterTutee = 0
    else:
      waitingBeforeTutee = tuteeTurn - 1
      waitingAfterTutee = totalWaiting - tuteeTurn

    ctx = {
        'user' : request.user,
        'waitingTutee' : waitingTutee,
        'waitingList' : waitingList,
        'waitingBeforeTutee' : waitingBeforeTutee,
        'tuteeTurn' : tuteeTurn,
        'waitingAfterTutee' : waitingAfterTutee,
        'totalWaiting' : totalWaiting,
        'pk' : pk,
    }

    return render(request, 'matching/waiting_room.html', ctx)

from django.views.decorators.http import require_POST

@login_required
@require_POST # 해당 뷰는 POST method 만 받는다.
def not_waiting(request):
    pk = request.POST.get('pk', None) # ajax 통신을 통해서 template에서 POST방식으로 전달
    log_pk = request.POST.get('log_pk', None)

    try:
        log = matching_models.SessionLog.objects.get(pk=log_pk)
    except matching_models.SessionLog.DoesNotExist:
        log = None

    if log:
        log.is_waiting = False
        log.save()

    context = {
       'message': "튜터링 대기열에서 제외되었습니다.",
    }

    return HttpResponse(json.dumps(context), content_type="application/json")
    # context를 json 타입으로

@login_required
@require_POST 
def set_attending_type(request):
  pk = request.POST.get('pk', None)
  online = request.POST.get('online', None)

  session = matching_models.TutorSession.objects.get(pk=pk)

  try:
      log = matching_models.SessionLog.objects.get(tutee = request.user, tutor_session = session, is_waiting = True)
  except matching_models.SessionLog.DoesNotExist:
      print("LOG DOES NOT EXIST")
      log = None
  
  context = {}
  if log:
    if online == "true":
      print("ONLINE")
      log.attend_online = True
      log.save()
      context['message'] = "세션을 온라인으로 참석합니다."
    else:
      print("OFFLINE")
      log.attend_online = False
      log.save()
      context['message'] = "세션을 오프라인으로 참석합니다."
  else:
    context['message'] = "로그가 존재하지 않습니다."
  
  return HttpResponse(json.dumps(context), content_type="application/json")
    
