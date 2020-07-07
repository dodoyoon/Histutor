from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.db.models import F
from django.views import generic

from .models import Post, Topic
from .forms import PostForm


class IndexView(generic.ListView):
    template_name = 'matching/main.html'
    def get_queryset(self):
        #returns the last five published questions
        return Post.objects.order_by('-pub_date')[:5]

<<<<<<< HEAD
def tutorReport(request):
    report = Post.objects.last()

    return render(request, 'matching/tutor_report.html', {'report': report})
=======

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
