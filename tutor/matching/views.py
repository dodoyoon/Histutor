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
from django.views.generic.edit import UpdateView
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

    def get_object(self):
        report = get_object_or_404(Report, pk=self.kwargs['pk'])
        return report


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

@login_required(login_url=URL_LOGIN)
def report_detail(request, pk):
    report = matching_models.Report.objects.get(pk=pk)
    if request.method == "POST":
        form = AccuseForm(request.POST)
        if form.is_valid():
            print("report accuse")

            report.tutee_feedback = form.cleaned_data['tutee_feedback']
            report.save()
            print("null? ", report.tutee_feedback == None)
            return redirect('matching:report_detail', pk=report.pk)
    else:
        form = AccuseForm()

    ctx = {
        'user' : request.user,
        'report': report,
        'form' : form,
    }

    return render(request, 'matching/report_detail.html', ctx)

@login_required(login_url=URL_LOGIN)
def post_new(request):
    ctx={}
    if request.method == "POST":
        form = PostForm(request.POST)
        if form.is_valid():
            print('form data : ', form.cleaned_data) ;
            post = form.save(commit=False)
            user_obj = matching_models.User.objects.get(username=request.user.username)
            post.user = user_obj
            post.finding_match = True
            post.save()
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

    ctx['post'] = post

    if hasattr(post, 'report'):
        ctx['report_exist'] = True ;
    else:
        ctx['report_exist'] = False ;

    cmt = matching_models.Comment.objects.filter(post=post)
    ctx['cmt'] = cmt

    if request.method == "POST":
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.user = request.user
            comment.post = post
            comment.save()
            return redirect('matching:post_detail', pk=post.pk)
    else:
        cancel_form = CancelForm()
        form = CommentForm()

    if request.user == post.user:
        ctx['showbut'] = True
    else:
        ctx['showbut'] = False

    if post.tutor is None:
        ctx['hastutor'] = False
    else:
        ctx['hastutor'] = True

    ctx['form'] = form
    ctx['cancel_form'] = cancel_form ;

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
            post.topic = form.cleaned_data['topic']
            post.title = form.cleaned_data['title']
            post.content = form.cleaned_data['content']
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

    report = matching_models.Post.objects.filter(tutor=request.user).filter(report__isnull=True)
    #print(report)

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
        'reports': report,
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
    post = matching_models.Post.objects.filter(user=request.user)

    if hasattr(post, 'report'):
        ctx['report_exist'] = True ;
    else:
        ctx['report_exist'] = False ;

    print(">>> report_exist: ")
    print(ctx['report_exist'])

    recruiting = post.filter(finding_match = True).order_by('-pub_date')
    recruited = post.filter(finding_match = False).order_by('-pub_date')
    #posts = tutor_models.Post.objects.order_by('-pub_date')
    posts = list(chain(recruiting, recruited))

    report = matching_models.Report.objects.filter(tutor=request.user).order_by('-pub_date')
    print(report)

    empty_report = matching_models.Post.objects.filter(tutor=request.user).filter(report__isnull=True)

    ctx = {
        'posts' : posts,
        'reports': report,
        'emptyreports': empty_report,
    }
    return render(request, 'matching/mypage.html', ctx)
