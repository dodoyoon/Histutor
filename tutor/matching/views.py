from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django.db.models import F
from django.views import generic
from .models import Post

class IndexView(generic.ListView):
    template_name = 'matching/main.html'
    def get_queryset(self):
        #returns the last five published questions
        return Post.objects.order_by('-pub_date')[:5]

def tutorReport(request):
    report = Post.objects.last()

    return render(request, 'matching/tutor_report.html', {'report': report})
