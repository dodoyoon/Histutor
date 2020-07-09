from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.db.models import F
from django.views import generic
from .models import Post, Topic, Profile
from django.contrib.auth.models import User
from .forms import PostForm, ReportForm, ProfileForm
from django.contrib.auth.decorators import login_required
from django.db import transaction

class IndexView(generic.ListView):
    template_name = 'matching/main.html'
    def get_queryset(self):
        #returns the last five published questions
        return Post.objects.order_by('-pub_date')[:5]

@login_required
@transaction.atomic
def save_profile(request, pk):
    if request.method == 'POST':
        user = User.objects.get(pk=pk)
        profile_form = ProfileForm(request.POST, instance= user.profile)
        if profile_form.is_valid():
            profile = profile_form.save(commit=False)
            profile.signin = True
            profile.save()
            return redirect('/matching') # redirect으로 tutee home으로 이동
    else:
        profile_form = ProfileForm(instance=request.user.profile)
    return render(request, 'matching/signup.html', {
        'profile_form' : profile_form
    })

def user_check(request):
    
    if "handong.edu" in request.user.email:
        print("handong student")
        try:
            user = User.objects.get(pk=request.user.pk)
            if user.profile.signin == False:
                print("redirect to signin page")
                return HttpResponseRedirect(reverse('matching:profile', args=(request.user.pk,)))
            elif user.profile.is_tutor is True: #TODO : redirect to tutor_home
                return HttpResponseRedirect(reverse('matching:index'))
            else:
                return HttpResponseRedirect(reverse('matching:index')) #TODO : redirect to tutee_home
        except(KeyError, User.DoesNotExist):
            return HttpResponseRedirect(reverse('matching:index'))
    else:
        print("not valid email address")
        User.objects.filter(pk=request.user.pk).delete()
        return HttpResponseRedirect(reverse('matching:index'))

def tutorReport(request):
    post = Post.objects.last()
    if request.method == "POST":
        form = ReportForm(request.POST)
        if form.is_valid():
            report = form.save(commit=False)
            report.tutor = User.objects.last()
            report.tutee = User.objects.get(id = post.user.id)
            report.post = Post.objects.get(id = post.id)
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

    topic_list = Topic.objects.all()
    ctx['topic_list'] = topic_list

    if request.method == "POST":
        form = PostForm(request.POST)

        if form.is_valid():
            topic = request.POST['topic']
            post = form.save(commit=False)
            post.topic = Topic.objects.get(name=topic)
            user_obj = User.objects.get(name=request.user.username)
            post.user = user_obj
            post.save()
            # return redirect('post_detail', pk=post.pk)
    else:
        form = PostForm()


    ctx['form'] = form

    return render(request, 'matching/post_edit.html', ctx)
