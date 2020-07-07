from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.db.models import F
from django.views import generic
<<<<<<< HEAD

from .models import Post, Topic, User
from .forms import PostForm, ReportForm

=======
from .models import User, Post, Topic
from .forms import SignupForm, PostForm
>>>>>>> 8fc4fb73b74c49c4d3543be6aec6020600369c14

class IndexView(generic.ListView):
    template_name = 'matching/main.html'
    def get_queryset(self):
        #returns the last five published questions
        return Post.objects.order_by('-pub_date')[:5]

<<<<<<< HEAD
=======
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

>>>>>>> 8fc4fb73b74c49c4d3543be6aec6020600369c14
def tutorReport(request):
    if request.method == "POST":
        form = ReportForm(request.POST)
        if form.is_valid():
            print("VALID")
            post = form.save(commit=False)
            post.tutor = User.objects.last()
            post.tutee = User.objects.last()
            post.post = Post.objects.last()
            post.tutee_feedback = "asdasdasd"
            post.save()
        else:
            print("NOT VALID")
    else: 
        form = ReportForm()

    report = Post.objects.last()
    ctx = {
        'report': report,
        'form': form,
    }

<<<<<<< HEAD
    return render(request, 'matching/tutor_report.html', ctx)
=======
    return render(request, 'matching/tutor_report.html', {'report': report})
>>>>>>> 8fc4fb73b74c49c4d3543be6aec6020600369c14

def post_new(request):
    ctx={}

    if request.method == "POST":
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            # post.author = request.user
            # post.published_date = timezone.now()
            post.save()
            # return redirect('post_detail', pk=post.pk)
    else:
        form = PostForm()


    ctx['form'] = form

    return render(request, 'matching/post_edit.html', ctx)
