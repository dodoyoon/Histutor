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

@login_required
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
            profile.save()
            return redirect('/matching') # redirect으로 tutee home으로 이동
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
                print("redirect to signin page")
                return HttpResponseRedirect(reverse('matching:profile', args=(request.user.pk,)))
            elif user.profile.is_tutor is True: #TODO : redirect to tutor_home
                return HttpResponseRedirect(reverse('matching:index'))
            else:
                return HttpResponseRedirect(reverse('matching:index')) #TODO : redirect to tutee_home
        except(KeyError, matching_models.User.DoesNotExist):
            return HttpResponseRedirect(reverse('matching:index'))
    else:
        print("not valid email address")
        matching_models.User.objects.filter(pk=request.user.pk).delete()
        return HttpResponseRedirect(reverse('matching:index'))

def tutor_report(request, pk):
    if not request.user.is_authenticated:
        return redirect('/accounts/login/')

    post = matching_models.Post.objects.get(pk=pk)

    if request.user.profile.id != post.tutor.profile.id:
        if request.user.profile.is_tutor == True:
            return redirect('matching:tutor_home')
        else:
            return redirect('matching:tutee_home')

    if request.method == "POST":
        form = ReportForm(request.POST)
        if form.is_valid():
            report = form.save(commit=False)
            report.tutor = matching_models.User.objects.last()
            report.tutee = matching_models.User.objects.get(id = post.user.id)
            report.post = matching_models.Post.objects.get(id = post.id)
            report.save()
            return redirect('matching:report_detail', pk=report.pk)
    else:
        form = ReportForm()

    ctx = {
        'post': post,
        'form': form,
    }

    return render(request, 'matching/tutor_report.html', ctx)

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
    if request.user.pk == report.tutee.pk:
        is_post_writer = True
    else: 
        is_post_writer = False
    ctx = {
        'report': report,
        'form' : form,
        'is_post_writer' : is_post_writer,
    }

    return render(request, 'matching/report_detail.html', ctx)

def post_new(request):
    if not request.user.is_authenticated:
        return redirect('/accounts/login/')

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

def post_detail(request, pk):
    if not request.user.is_authenticated:
        return redirect('/accounts/login/')

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
        print("********************post_detail , post")
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.user = request.user
            comment.post = post
            comment.save()
            #print(">>> pk: " + str(post.pk))
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


def post_edit(request, pk):
    if not request.user.is_authenticated:
        return redirect('/accounts/login/')

    ctx={}
    post = matching_models.Post.objects.get(pk=pk)

    if post.user.profile.id != request.user.profile.id:
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


def tutee_home(request):
    if not request.user.is_authenticated:
        return redirect('/accounts/login/')
    else:
        post = matching_models.Post.objects.filter(user = request.user, finding_match = True)
        if not post:
            return render(request, 'matching/tutee_home.html', {})
        else:
            return redirect('matching:post_detail', pk=post[0].pk)

def tutor_home(request):
    if not request.user.is_authenticated:
        return redirect('/accounts/login/')


    user = matching_models.User.objects.get(pk=request.user.pk)

    if not user.profile.is_tutor is True:
        return redirect(reverse('matching:tutee_home'))

    report = matching_models.Post.objects.filter(tutor=request.user).filter(report__isnull=True)
    #print(report)

    recruiting = matching_models.Post.objects.filter(finding_match = True).order_by('-pub_date')
    recruited = matching_models.Post.objects.filter(finding_match = False).order_by('-pub_date')
    #posts = tutor_models.Post.objects.order_by('-pub_date')
    posts = list(chain(recruiting, recruited))

    ctx = {
        'posts': posts,
        'reports': report,
    }

    return render(request, 'matching/tutor_home.html', ctx)


def admin_home(request):
    if not request.user.is_authenticated:
        return redirect('/accounts/login/')


    user = matching_models.User.objects.get(pk=request.user.pk)

    print(user.is_staff)

    if not user.is_staff:
        return redirect(reverse('matching:tutee_home'))


    recruiting = matching_models.Post.objects.filter(finding_match = True).order_by('-pub_date')
    recruited = matching_models.Post.objects.filter(finding_match = False).order_by('-pub_date')
    #posts = tutor_models.Post.objects.order_by('-pub_date')
    posts = list(chain(recruiting, recruited))

    ctx = {
        'posts': posts,
    }

    return render(request, 'matching/admin_home.html', ctx)


def tutee_accept_report(request):
    report = matching_models.Report.objects.last()
    print(report)
    if request.method == "POST":
        acceptForm = AcceptReportForm(request.POST, instance=report)
        if acceptForm.is_valid():
            report = acceptForm.save(commit=False)
            report.is_confirmed = True
            report.save()
    else:
        acceptForm = AcceptReportForm()

    ctx = {
        'report': report,
        'form': acceptForm,
    }

    return render(request, 'matching/tutee_accept_report.html', ctx)

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

def mypage(request):
    post = matching_models.Post.objects.filter(user=request.user)

    recruiting = post.filter(finding_match = True).order_by('-pub_date')
    recruited = post.filter(finding_match = False).order_by('-pub_date')
    #posts = tutor_models.Post.objects.order_by('-pub_date')
    posts = list(chain(recruiting, recruited))

    report = matching_models.Report.objects.filter(tutor=request.user).order_by('-pub_date')
    #print(report)

    empty_report = matching_models.Post.objects.filter(tutor=request.user).filter(report__isnull=True)

    ctx = {
        'posts' : posts,
        'reports': report,
        'emptyreports': empty_report,
    }
    return render(request, 'matching/mypage.html', ctx)
