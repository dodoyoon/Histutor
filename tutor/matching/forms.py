from django import forms
from .models import Post, Topic, Report, User
from django.forms import ModelChoiceField

class SignupForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['name', 'student_number','nickname', 'phone', 'email']

class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['title', 'content']

class ReportForm(forms.ModelForm):
    class Meta:
        model = Report
        fields = ('meeting_date','meeting_duration_time','content')
