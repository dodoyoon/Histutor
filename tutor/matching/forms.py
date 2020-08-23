from django import forms
from .models import Post, Report, Comment
from django.forms import ModelChoiceField

class AccuseForm(forms.ModelForm):
    class Meta:
        model = Report
        fields = ['join_tutee', 'content']

class PostForm(forms.ModelForm):
    title = forms.CharField(widget=forms.TextInput(attrs={'size': '50', 'placeholder': '예) MySQL 설치하는데 자꾸 오류가 떠요', 'minlength': '15'}))
    class Meta:
        model = Post
        fields = ['title']

class TutorReportForm(forms.ModelForm):
    class Meta:
        model = Report
        fields = ['join_tutee', 'content']

    def __init__(self, *args, **kwargs):
        super(TutorReportForm, self).__init__(*args, **kwargs)
        self.fields['content'].widget.attrs.update({'name' : 'content'})

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
