from django import forms
from .models import Post, Report, Profile, Comment
from django.forms import ModelChoiceField

class AccuseForm(forms.ModelForm):
    class Meta:
        model = Report
        fields = ['tutee_feedback']

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['nickname']

class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['title']

class DateInput(forms.DateInput):
    input_type = 'date'



class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('content',)

class AcceptReportForm(forms.ModelForm):
    class Meta:
        model = Report
        fields = ('tutee_feedback',)
