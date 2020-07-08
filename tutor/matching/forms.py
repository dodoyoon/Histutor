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
        fields = ('topic', 'title', 'content')

    def __init__(self, *args, **kwargs):
        super(PostForm, self).__init__(*args, **kwargs)
        self.fields['topic']=forms.ModelChoiceField(queryset=Topic.objects.all())

class ReportForm(forms.ModelForm):
    class Meta:
        model = Report
        fields = ('meeting_date','meeting_duration_time','content')
