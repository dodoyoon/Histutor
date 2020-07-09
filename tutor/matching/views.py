from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.db.models import F
from django.views import generic
from itertools import chain

from matching import models as tutor_models
from .forms import PostForm, ReportForm, SignupForm


# DEFAULT PAGE
def index(request):
    if request.user.is_authenticated:
        return redirect('tutee_home/')
    else:
        return redirect('/accounts/login/')

def signup(request):
    if request.method == 'POST':
        form = SignupForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save(commit=False)
            user.save()
            return redirect('/matching') # redirect으로 tutee home으로 이동
    else:
        form = SignupForm()
    return render(request, 'matching/signup.html', {
        'form' : form,
    })

def tutorReport(request):
    post = tutor_models.Post.objects.last()
    if request.method == "POST":
        form = ReportForm(request.POST)
        if form.is_valid():
            report = form.save(commit=False)
            report.tutor = tutor_models.User.objects.last()
            report.tutee = tutor_models.User.objects.get(id = post.user.id)
            report.post = tutor_models.Post.objects.get(id = post.id)
            report.save()
    else:
        form = ReportForm()

    ctx = {
        'post': post,
        'form': form,
    }

    return render(request, 'matching/tutor_report.html', ctx)

def post_new(request):
    ctx={}

    topic_list = tutor_models.Topic.objects.all()
    ctx['topic_list'] = topic_list

    if request.method == "POST":
        form = PostForm(request.POST)

        if form.is_valid():
            topic = request.POST['topic']
            post = form.save(commit=False)
            post.topic = tutor_models.Topic.objects.get(name=topic)
            user_obj = tutor_models.User.objects.get(name=request.user.username)
            post.user = user_obj
            post.finding_match = True
            post.save()
            print(">>> pk: " + str(post.pk))
            return redirect('matching:post_detail', pk=post.pk)
    else:
        form = PostForm()


    ctx['form'] = form

    return render(request, 'matching/post_new.html', ctx)

def post_detail(request, pk):
    ctx={}

    try:
        post = get_object_or_404(tutor_models.Post, pk=pk)
    except Notice.DoesNotExist:
        return HttpResponse("채용공고가 없습니다.")

    ctx['post'] = post

    return render(request, 'matching/post_detail.html', ctx)

def tutee_home(request):
    return render(request, 'matching/tutee_home.html', {})

def tutor_home(request):
    recruiting = tutor_models.Post.objects.filter(finding_match = True).order_by('-pub_date')
    recruited = tutor_models.Post.objects.filter(finding_match = False).order_by('-pub_date')
    #posts = tutor_models.Post.objects.order_by('-pub_date')
    posts = list(chain(recruiting, recruited))

    ctx = {
        'posts': posts,
    }

    return render(request, 'matching/tutor_home.html', ctx)
