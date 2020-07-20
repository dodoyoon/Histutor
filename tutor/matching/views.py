from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.db.models import F
from django.views import generic
from django.contrib.auth.models import User
from .forms import PostForm, ReportForm, ProfileForm, CommentForm, AcceptReportForm, CancelForm, AccuseForm
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

URL_LOGIN = "/matching"
# DEFAULT PAGE

def index(request):
    if request.user.is_authenticated:
        user = matching_models.User.objects.get(pk=request.user.pk)
        if not user.profile.is_tutor is True:
            return redirect(reverse('matching:tutee_home'))
        else:
            return redirect(reverse('matching:tutor_home'))
    else:
        return redirect('login/')

def login(request):
    return render(request, 'matching/account_login.html', {})

@login_required(login_url=URL_LOGIN)
@transaction.atomic
def save_profile(request, pk):
    if not request.user.is_authenticated:
        return redirect('/accounts/login/')
    if request.method == 'POST':
        user = matching_models.User.objects.get(pk=pk)
        profile_form = ProfileForm(request.POST, instance= user.profile)
        if profile_form.is_valid():
            profile = profile_form.save(commit=False)
            profile.signin = True
            profile.phone = "010" + str(request.POST['phone1']) + str(request.POST['phone2'])
            profile.save()
            return redirect(reverse('matching:tutee_home'))
    else:
        profile_form = ProfileForm(instance=request.user.profile)
    return render(request, 'matching/save_profile.html', {
        'profile_form' : profile_form
    })

def user_check(request):

    if "handong.edu" in request.user.email:
        print("handong student")
        try:
            user = matching_models.User.objects.get(pk=request.user.pk)
            if user.profile.signin == False:
                return HttpResponseRedirect(reverse('matching:profile', args=(request.user.pk,)))
            elif user.profile.is_tutor is True:
                return HttpResponseRedirect(reverse('matching:tutor_home'))
            else:
                return HttpResponseRedirect(reverse('matching:tutee_home'))
        except(KeyError, matching_models.User.DoesNotExist):
            return HttpResponseRedirect(reverse('matching:index'))
    else:
        print("not valid email address")
        matching_models.User.objects.filter(pk=request.user.pk).delete()
        return HttpResponseRedirect(reverse('matching:index'))

#TODO : method decorator should be added
class ReportUpdate(UpdateView):
    model = Report
    context_object_name = 'report'
    form_class = ReportForm
    template_name = 'matching/report_edit.html'

@login_required(login_url=URL_LOGIN)
def tutor_report(request, pk):
    post = matching_models.Post.objects.get(pk=pk)

    if request.user.pk != post.tutor.pk :
        if request.user.profile.is_tutor == True:
            return redirect('matching:tutor_home')
        else:
            return redirect('matching:tutee_home')

    if request.method == "POST":
        form = ReportForm(request.POST)
        if form.is_valid():
            print("report form valid")
            report = form.save(commit=False)
            report.tutor = matching_models.User.objects.get(pk = request.user.pk)
            report.tutee = matching_models.User.objects.get(pk = post.user.pk)
            report.post = matching_models.Post.objects.get(pk = post.pk)
            report.save()
            return redirect('matching:report_detail', pk=report.pk)
        else:
            print("report form *invalid*")

    else:
        form = ReportForm()

    ctx = {
        'post': post,
        'form': form,
    }

    return render(request, 'matching/tutor_report.html', ctx)

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
    ctx={}
    if request.method == "POST":
        form = PostForm(request.POST)
        if form.is_valid():
            print('form data : ', form.cleaned_data)
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

    user = matching_models.User.objects.get(pk=request.user.pk)
    ctx['user'] = user

    try:
        post = get_object_or_404(matching_models.Post, pk=pk)
    except post.DoesNotExist:
        return HttpResponse("포스트가 없습니다.")
    except matching_models.Post.DoesNotExist:
        return HttpResponse("게시물이 존재하지 않습니다.")

    if hasattr(post, 'report'):
        ctx['report_exist'] = True ;
    else:
        ctx['report_exist'] = False ;

    comment_list = matching_models.Comment.objects.filter(post=post)

    ctx['post'] = post
    ctx['comment_list'] = comment_list

    return render(request, 'matching/post_detail.html', ctx)

def set_tutor(request, postpk, userpk):
    try:
        post = get_object_or_404(matching_models.Post, pk=postpk)
    except post.DoesNotExist:
        return HttpResponse("포스트가 없습니다.")

    try:
        tutor = get_object_or_404(User, pk=userpk)
    except tutor.DoesNotExist:
        return HttpResponse("사용자가 없습니다.")

    post.tutor = tutor
    post.finding_match = False
    post.save()

    return redirect('matching:post_detail', pk=post.pk)

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
def tutee_home(request):
    post = matching_models.Post.objects.filter(user = request.user, finding_match = True)
    if not post:
        return render(request, 'matching/tutee_home.html', {})
    else:
        return redirect('matching:post_detail', pk=post[0].pk)

@login_required(login_url=URL_LOGIN)
def tutor_home(request):
    user = matching_models.User.objects.get(pk=request.user.pk)

    if not user.profile.is_tutor is True:
        return redirect(reverse('matching:tutee_home'))

    if request.method == "POST":
        form = PostForm(request.POST)
        if form.is_valid():
            print('form data : ', form.cleaned_data)
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

    report = matching_models.Post.objects.filter(tutor=request.user).filter(report__isnull=True)
    #print(report)

    recruiting = matching_models.Post.objects.filter(finding_match = True).order_by('-pub_date')
    recruited = matching_models.Post.objects.filter(finding_match = False).order_by('-pub_date')
    #posts = tutor_models.Post.objects.order_by('-pub_date')
    posts = list(chain(recruiting, recruited))

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
        'posts': posts,
        'reports': report,
        'postPaginator': post_paginator,
        'paginatorRange': paginatorRange,
        'form': form,
    }

    return render(request, 'matching/tutor_home.html', ctx)

@login_required(login_url=URL_LOGIN)
def admin_home(request):
    user = matching_models.User.objects.get(pk=request.user.pk)

    print(user.is_staff)

    if not user.is_staff:
        return redirect(reverse('matching:tutee_home'))


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

    ctx = {
        'posts': posts,
    }

    return render(request, 'matching/admin_home.html', ctx)


def close_post(request, pk):
    if request.method == 'POST':
        print("close_post : POST")
        form = CancelForm(request.POST, request.FILES)
        if form.is_valid():
            print("form valid")
            post = matching_models.Post.objects.get(pk=pk)
            post.cancel_reason = form.cleaned_data['cancel_reason']
            post.finding_match = False
            post.save()
            return redirect(reverse('matching:tutee_home'))
        else:
            print("form invalid")

    else:
        print("close_post : GET")
        form = CancelForm()
        return render(request, 'matching/post_detail.html')


@login_required(login_url=URL_LOGIN)
def mypage(request):
    ctx = {}

    print(request.user.profile.is_tutor)
    if request.user.profile.is_tutor:
        return redirect(reverse('matching:mypage_report'))
    elif request.user.is_staff:
        pass
    else:
        return redirect(reverse('matching:mypage_post'))

    return render(request, 'matching/mypage.html', ctx)

@login_required(login_url=URL_LOGIN)
def mypage_post(request):
    ctx = {}
    post = matching_models.Post.objects.filter(user=request.user)

    recruiting = post.filter(finding_match = True).order_by('-pub_date')
    recruited = post.filter(finding_match = False).order_by('-pub_date')
    #posts = tutor_models.Post.objects.order_by('-pub_date')
    posts = list(chain(recruiting, recruited))

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

    report = matching_models.Report.objects.filter(tutor=request.user).order_by('-pub_date')

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
def mypage_incomplete(request):
    ctx = {}

    empty_report = matching_models.Post.objects.filter(tutor=request.user).filter(report__isnull=True)
    ctx['emptyreports'] = empty_report

    return render(request, 'matching/mypage_incomplete.html', ctx)

'''
def index(request):
    return render(request, 'matching/index.html', {})

def room(request, room_name):
    return render(request, 'matching/room.html', {
        'room_name': room_name
    })
'''
