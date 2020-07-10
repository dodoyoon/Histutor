from django import forms
from .models import Post, Report, Profile, Comment
from django.forms import ModelChoiceField


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['nickname','phone'] 

class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['title', 'topic','content']

class ReportForm(forms.ModelForm):
    class Meta:
        model = Report
        fields = ('meeting_date','meeting_duration_time','content')

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('content',)

class AcceptReportForm(forms.ModelForm):
    class Meta:
        model = Report
        fields = ('tutee_feedback',)

