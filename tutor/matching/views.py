from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.db.models import F
from django.views import generic
from django.contrib.auth.models import User
from .forms import PostForm, CommentForm, AcceptReportForm, AccuseForm, ReportForm
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

URL_LOGIN = "/matching"
# DEFAULT PAGE

def index(request):
    if request.user.is_authenticated:
        return redirect('matching:mainpage')
    else:
        return redirect('login/')

def login(request):
    return render(request, 'matching/account_login.html', {})


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
                user.profile.nickname =user.username[1:2] + user.last_name
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

    if request.method == "POST":
        form = ReportForm(request.POST)

        if form.is_valid():
            report = form.save(commit=False)
            report.tutor = matching_models.User.objects.get(pk = post.tutor.pk)
            report.tutee = matching_models.User.objects.get(pk = post.user.pk)
            report.post = matching_models.Post.objects.get(pk = post.pk)
            report.save()
            return redirect('matching:report_detail', pk=report.pk)
        else:
            return redirect('matching:mainpage')

class ReportDetail(DetailView):
    model = Report

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


@login_required(login_url=URL_LOGIN)
def post_new(request):
    if request.method == "POST":
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            user_obj = matching_models.User.objects.get(username=request.user.username)
            post.user = user_obj
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
        messages.error(request, '해당 게시물은 존재하지 않습니다.')
        return HttpResponseRedirect(reverse('matching:mainpage'))

    user = matching_models.User.objects.get(username=request.user.username)
    report_to_write = matching_models.Post.objects.filter(user=user, pk=pk, report__isnull=True, tutor__isnull=False)

    if report_to_write.exists():
        for report in report_to_write:
            report_form = ReportForm()
            ctx['report_form'] = report_form
            ctx['report_exist'] = True
            ctx['report_post_pk'] = report.pk

    comment_list = matching_models.Comment.objects.filter(post=post).order_by('pub_date')

    ctx['post'] = post
    ctx['comment_list'] = comment_list
    ctx['start_msg'] = ""
    if post.finding_match is False and post.tutor:
        print(post.tutor)
        ctx['start_msg'] = post.tutor.last_name+post.user.last_name+"튜터링시작"
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

    if tutor.pk == post.user.pk:
        #포스트 작성자가 직접 튜터가 될 수 없음.
        return redirect('matching:post_detail', pk=post.pk)
    post.tutor = tutor
    post.finding_match = False
    post.start_time = timezone.localtime()
    post.save()

    start_tutoring_cmt = matching_models.Comment(user=tutor, post=post, pub_date=post.start_time, content=tutor.last_name+post.user.last_name+"튜터링시작")
    start_tutoring_cmt.save()

    return redirect('matching:post_detail', pk=post.pk)

@login_required
def send_message(request):
    if request.method == "GET":
        post = matching_models.Post.objects.get(pk=request.GET['postid'])
        new_cmt = matching_models.Comment(user=request.user, post=post, pub_date=timezone.now(), content=request.GET['content'])
        new_cmt.save()
        return HttpResponse(new_cmt.id)
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
def admin_home(request):
    user = matching_models.User.objects.get(pk=request.user.pk)

    if not user.is_staff:
        return redirect(reverse('matching:mainpage'))

    recruiting = matching_models.Post.objects.filter(finding_match = True).order_by('-pub_date')
    recruited = matching_models.Post.objects.filter(finding_match = False).order_by('-pub_date')
    #posts = tutor_models.Post.objects.order_by('-pub_date')
    posts = list(chain(recruiting, recruited))

    post_page = request.GET.get('page', 1)

    post_paginator = Paginator(posts, 10)
    try:
        posts = post_paginator.page(post_page)
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
        'posts': posts,
        'paginatorRange': paginatorRange,
    }

    return render(request, 'matching/admin_home.html', ctx)


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
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            user_obj = matching_models.User.objects.get(username=request.user.username)
            post.user = user_obj
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

            title = post.title
            url = "http://" + request.get_host() + reverse('matching:post_detail', args=[post.pk])
            payload = '{"body":"New Post has been posted.","connectColor":"#6C639C","connectInfo":[{"title":"' + title + '","imageUrl":"' + url + '"}]}'

            headers = {'Accept': 'application/vnd.tosslab.jandi-v2+json',
            'Content-Type': 'application/json'}

            r = requests.post("https://wh.jandi.com/connect-api/webhook/20949533/4bbee5c811038e410ccea15513acd716", data=payload.encode('utf-8'), headers=headers)
            return redirect('matching:post_detail', pk=post.pk)
    else:
        form = PostForm()


    ### 튜터링 검색기능 ###
    search_word = request.GET.get('search_word', '') # GET request의 인자중에 q 값이 있으면 가져오고, 없으면 빈 문자열 넣기

    if search_word != '': # q가 있으면
        recruiting = matching_models.Post.objects.filter(finding_match = True, title__icontains=search_word).order_by('-pub_date')
        onprocess = matching_models.Post.objects.filter(start_time__isnull = False, fin_time__isnull = True, title__icontains=search_word).order_by('-pub_date')
        recruited = matching_models.Post.objects.filter(finding_match = False, title__icontains=search_word).order_by('-pub_date')
        recruited = recruited.exclude(start_time__isnull = False, fin_time__isnull = True)
    else:
        recruiting = matching_models.Post.objects.filter(finding_match = True).order_by('-pub_date')
        onprocess = matching_models.Post.objects.filter(start_time__isnull = False, fin_time__isnull = True).order_by('-pub_date')
        recruited = matching_models.Post.objects.filter(finding_match = False).order_by('-pub_date')
        recruited = recruited.exclude(start_time__isnull = False, fin_time__isnull = True)

    #posts = tutor_models.Post.objects.order_by('-pub_date')
    posts = list(chain(recruiting, onprocess, recruited))

    current_post_page = request.GET.get('page', 1)

    post_paginator = Paginator(posts, 9)
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
        'ongoing_tutoring' : ongoing_tutoring,
        'ongoing_post': ongoing_post,
        'user': user,
        'posts': posts,
        'postPaginator': post_paginator,
        'paginatorRange': paginatorRange,
        'form': form,
        'post_exist': post_exist,
        'today' : timezone.localtime(),
    }

    # Tutee Report Part
    user_obj2 = matching_models.User.objects.get(username=request.user.username)

    report_to_write = matching_models.Post.objects.filter(user=user_obj2, report__isnull=True, tutor__isnull=False)

    if report_to_write.exists():
        for report in report_to_write:
            report_form = ReportForm()
            ctx['report_form'] = report_form
            ctx['report_exist'] = True
            ctx['report_post_pk'] = report.pk

    return render(request, 'matching/main.html', ctx)
