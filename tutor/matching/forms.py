from django import forms
from .models import Post, Report, Comment
from django.forms import ModelChoiceField

class AccuseForm(forms.ModelForm):
    class Meta:
        model = Report
        fields = ['content']

class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['title']

class ReportForm(forms.ModelForm):
    class Meta:
        model = Report
        fields = ['content']

    def __init__(self, *args, **kwargs):
        super(ReportForm, self).__init__(*args, **kwargs)
        self.fields['content'].widget.attrs.update({'name' : 'content'})

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('content',)

class AcceptReportForm(forms.ModelForm):
    class Meta:
        model = Report
        fields = ('content',)
